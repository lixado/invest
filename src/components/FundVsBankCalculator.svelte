<script lang="ts">
    import { onMount } from 'svelte';
    import type { FundResult, Bank, AutocompleteOption } from '../utils/models';
    import AutocompleteSelector from './AutocompleteSelector.svelte';

    var fundsData: FundResult[];
    var banksData: Bank[];

    var startAmount = formatNumber("10000");
    function getStartAmountValue(): number {
        return Number(startAmount.replace(/,/g, ''));
    }
    var monthlyContribution = formatNumber("1000");
    function getMonthlyContributionValue(): number {
        return Number(monthlyContribution.replace(/,/g, ''));
    }
    const futureYears = 2;
    var futureMonths = 1+ 12*futureYears; // number of years

    var showAddFundInput = false;
    var showAddBankInput = false;

    var funds: FundResult[] = [];
    var banks: Bank[] = [];


    function addFund(event: CustomEvent) {
        const option: AutocompleteOption = event.detail.option;
        funds.push(fundsData[option.index]);
        funds = funds; // Trigger reactivity

        showAddFundInput = false;
    }

    function addBank(event: CustomEvent) {
        const option: AutocompleteOption = event.detail.option;
        banks.push(banksData[option.index]);
        banks = banks; // Trigger reactivity

        showAddBankInput = false;
    }

    function formatNumber(value: string): string {
        return value.replace(/\D/g, '').replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    let inputElement: HTMLInputElement; // focus on input element on load
    $: if (showAddFundInput && inputElement) {
        inputElement.focus();
    }

    function calculateFund(fund: FundResult, months: number): number {
        /* months starts at 0 */
        if (months == 0) {
            return getStartAmountValue();
        }
        // recursive calculation of the fund's interest
        let fund_monthly_interest = (Number(fund.annual_growth_info.annual_growth_1y)/(100))/12;
        let fund_monthly_cost = (fund.fund_info.fund_calculated_fee/(100))/12; // it is actually charged daily
        let after_interest_after_cost =  (calculateFund(fund, months-1) * (1 + fund_monthly_interest)) * (1-fund_monthly_cost);
        return after_interest_after_cost + getMonthlyContributionValue();
    }

    function calculateBank(bank: Bank, months: number): number {
        /* months starts at 0 */
        if (months == 0) {
            return getStartAmountValue();
        }
        // recursive calculation of the bank's interest
        return calculateBank(bank, months-1) * (1 + (Number(bank.rentesats1)/100)) + getMonthlyContributionValue();
    }

    onMount(async () => {
        try {
            // get current url
            const currentUrl = window.location.href;

            // Read JSON from funds.json
            const fundsResponse = await fetch(currentUrl + '/funds.json');
            fundsData = await fundsResponse.json();

            // Read JSON from banks.json
            const banksResponse = await fetch(currentUrl + '/banks.json');
            banksData = await banksResponse.json();

            // for testing purposes fill in with 3 funds and 3 banks
            funds = fundsData.sort(() => 0.5 - Math.random()).slice(0, 2);
            banks = banksData.sort(() => 0.5 - Math.random()).slice(0, 2);
        } catch (error) {
            console.error('Error fetching stock price data:', error);
        }
    });
</script>

<main style="display: flex; flex-direction: column; align-items: center; height: 100vh; gap: 0.5em;">
    <h1 style="display: flex; align-items: center; justify-content: center;">
        <span>Funds</span>
        <span style="font-size: 5rem; margin: 0 1rem 0 1rem;">VS</span>
        <span>Banks</span>
    </h1>


    <div style="display: flex; flex-direction: row; gap: 0.5em; width: 50%;">
        <div style="display: flex; flex-direction: column; gap: 0.5em;">
            <label for="startAmount">Starting Amount:</label>
            <input type="text" id="startAmount" bind:value={startAmount} placeholder="Enter starting amount" on:input={(e) => startAmount = formatNumber(e.currentTarget.value)} />
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.5em;">
            <label for="monthlyContribution">Monthly Contribution:</label>
            <input type="text" id="monthlyContribution" bind:value={monthlyContribution} placeholder="Enter monthly contribution" on:input={(e) => monthlyContribution = formatNumber(e.currentTarget.value)} />
        </div>
    </div>

    <div style="display: flex; flex-direction: row; gap: 0.5em;">
        <button on:click={() => {showAddFundInput = true; showAddBankInput = false;}} class="add-button">
            <i class="fas fa-plus-circle"></i> Add Fund
        </button>
        <button on:click={() => {showAddBankInput = true; showAddFundInput = false;}} class="add-button">
            <i class="fas fa-plus-circle"></i> Add Bank
        </button>
    </div>
    
    {#if showAddFundInput}
        <div style="display: flex; align-items: center;">
            <AutocompleteSelector options={fundsData.map((fund, index) => ({
                index: index,
                name: fund.instrument_info.name,
                icon_url: fund.instrument_info.instrument_icon_url,
                interest_rate: fund.annual_growth_info.annual_growth_1y
            }))} on:select={addFund} />
        </div>
    {/if}
    {#if showAddBankInput}
    <div style="display: flex; align-items: center;">
        <AutocompleteSelector options={banksData.map((bank, index) => ({
            index: index,
            name: bank.leverandorVisningsnavn + ` (${bank.navn})`,
            icon_url: bank.leverandorUrl.endsWith('/') ? bank.leverandorUrl + 'favicon.ico' : bank.leverandorUrl + '/favicon.ico',
            interest_rate: Number(bank.rentesats1)
        }))} on:select={addBank} />
    </div>
    {/if}

    <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
        <div style="display: flex; flex-direction: column; gap: 0.5em; width: 100%;">
            {#each funds as fund}
                <div class="mat-card">
                    <img src={fund.instrument_info.instrument_icon_url} alt={fund.instrument_info.name} style="width: 50px; height: 50px;" />
                    <h3><a href={`https://www.nordnet.no/market/funds?sortField=yield_1y&sortOrder=descending&freeTextSearch=${fund.instrument_info.name}`} target="_blank">{fund.instrument_info.name}</a></h3>
                    <p>Calculated Fee: {fund.fund_info.fund_calculated_fee?.toFixed(2) ?? 'N/A'} %</p>
                    <p>Last 1 Year Increase: {fund.historical_returns_info.yield_1y?.toFixed(2) ?? 'N/A'}%</p>
                </div>
            {/each}
        </div>
        <span style="font-size: 5rem; margin: 0 1rem 0 1rem; align-self: center;">VS</span>
        <div style="display: flex; flex-direction: column; gap: 0.5em; width: 100%;">
            {#each banks as bank}
                <div class="mat-card" style="display: flex; flex-direction: column; align-items: center; height: 100%;">
                    <img src={bank.icon_url} alt={bank.leverandorVisningsnavn} style="width: 50px; height: 50px;" />
                    <h3><a href={`${bank.leverandorUrl}`} target="_blank">{bank.leverandorVisningsnavn + ` (${bank.navn})`}</a></h3>
                    <p>Interest Rate: {Number(bank.rentesats1)?.toFixed(2) ?? 'N/A'}%</p>
                </div>
            {/each}
        </div>
    </div>

    {#if funds.length > 0 && banks.length > 0}
        <div style="display: flex; flex-direction: column; gap: 0.5em; width: 100%;">
            <h1 style="text-align: center;">Comparison</h1>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        {#each funds as fund}
                            <th>
                                <div title={fund.instrument_info.name} style="display: flex; align-items: center; gap: 5px;">
                                    <img src={fund.instrument_info.instrument_icon_url} alt={fund.instrument_info.name} style="width: 20px; height: 20px;" />
                                    {fund.instrument_info.name.length > 10 ? fund.instrument_info.name.slice(0, 10) + '...' : fund.instrument_info.name}
                                </div>
                            </th>
                        {/each}
                        <th>VS</th>
                        {#each banks as bank}
                            <th>
                                <div title={bank.leverandorVisningsnavn} style="display: flex; align-items: center; gap: 5px;">
                                    <img src={bank.icon_url} alt={bank.leverandorVisningsnavn} style="width: 20px; height: 20px;" />
                                    {bank.leverandorVisningsnavn.length > 10 ? bank.leverandorVisningsnavn.slice(0, 10) + '...' : bank.leverandorVisningsnavn}
                                </div>
                            </th>
                        {/each}
                    </tr>
                </thead>
                <tbody>
                    {#each Array(futureMonths).fill(0).map((_, i) => {
                        const date = new Date();
                        date.setMonth(date.getMonth() + i);
                        return date;
                    }) as date, index}
                        <tr>
                            <td>{date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, ' ')}</td>
                            {#each funds as fund}
                            <td>{calculateFund(fund, index).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>  
                            {/each}
                            <td></td>
                            {#each banks as bank}
                                <td>{calculateBank(bank, index).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>  
                            {/each}
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {/if}
</main>

<style>
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 1rem;
        text-align: left;
        background-color: #2c2c2c;
        color: #fff;
    }

    th, td {
        padding: 0.75rem;
        border: 1px solid #444;
    }

    th {
        background-color: #444;
        font-weight: bold;
    }

    tr:nth-child(even) {
        background-color: #3a3a3a;
    }

    tr:hover {
        background-color: #555;
    }

    thead {
        background-color: #555;
    }

    tbody tr:hover {
        background-color: #666;
    }
</style>