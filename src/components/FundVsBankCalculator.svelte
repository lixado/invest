<script lang="ts">
    import { onMount } from 'svelte';
    import type { FundResult, Bank, AutocompleteOption } from '../utils/models';
    import AutocompleteSelector from './AutocompleteSelector.svelte';

    var fundsData: FundResult[];
    var banksData: Bank[] = [];

    var startAmount = formatNumber("10000");
    var monthlyContribution = formatNumber("1000");

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

    let inputElement: HTMLInputElement;
    $: if (showAddFundInput && inputElement) {
        inputElement.focus();
    }

    onMount(async () => {
        try {
            // Read JSON from funds.json
            const fundsResponse = await fetch('/funds.json');
            fundsData = await fundsResponse.json();

            // Read JSON from banks.json
            const banksResponse = await fetch('/banks.json');
            banksData = await banksResponse.json();
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


    <div class="input-container">
        <div class="input-group">
            <label for="startAmount">Starting Amount:</label>
            <input type="text" id="startAmount" bind:value={startAmount} placeholder="Enter starting amount" on:input={(e) => startAmount = formatNumber(e.currentTarget.value)} />
        </div>
        <div class="input-group">
            <label for="monthlyContribution">Monthly Contribution:</label>
            <input type="text" id="monthlyContribution" bind:value={monthlyContribution} placeholder="Enter monthly contribution" on:input={(e) => monthlyContribution = formatNumber(e.currentTarget.value)} />
        </div>
    </div>

    <div class="button-container">
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
        {#each funds as fund}
            <div class="mat-card">
                <img src={fund.instrument_info.instrument_icon_url} alt={fund.instrument_info.name} style="width: 100px; height: 100px;" />
                <h3><a href={`https://www.nordnet.no/market/funds?sortField=yield_1y&sortOrder=descending&freeTextSearch=${fund.instrument_info.name}`} target="_blank">{fund.instrument_info.name}</a></h3>
                <p>Calculated Fee: {fund.fund_info.fund_calculated_fee.toFixed(2)} %</p>
                <p>Last 1 Year Increase: {fund.historical_returns_info.yield_1y.toFixed(2)}%</p>
            </div>
        {/each}
    </div>
    <div style="display: flex; flex-direction: row; gap: 0.5em; width: 100%;">
        {#each banks as bank}
            <div class="mat-card">
                <img src={bank.leverandorUrl + 'favicon.ico'} alt={bank.leverandorVisningsnavn} style="width: 100px; height: 100px;" />
                <h3><a href={`${bank.leverandorUrl}`} target="_blank">{bank.leverandorVisningsnavn + ` (${bank.navn})`}</a></h3>
                <p>Interest Rate: {Number(bank.rentesats1).toFixed(2)}%</p>
            </div>
        {/each}
    </div>
</main>

<style>
    .input-container {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        width: 100%;
        max-width: 400px;
        margin-bottom: 1rem;
    }

    .input-group {
        display: flex;
        flex-direction: column;
        flex: 1;
        width: 0%;
    }

    .input-group label {
        margin-bottom: 0.5rem;
        font-weight: bold;
    }

    .input-group input {
        text-align: right;
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 1rem;
    }

    .input-group input:focus {
        outline: none;
        border-color: #1565c0;
        box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
    }
</style>