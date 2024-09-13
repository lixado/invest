<script lang="ts">
    import { onMount } from 'svelte';
    import { Chart , LineController, LineElement, PointElement, LinearScale, CategoryScale } from 'chart.js/auto';
    import zoomPlugin from 'chartjs-plugin-zoom';
    import AddIcon from 'virtual:icons/material-symbols/add';

    import type { FundResult, Bank, AutocompleteOption } from '../utils/models';
    import AutocompleteSelector from './AutocompleteSelector.svelte';
    import CardViewer from './CardViewer.svelte';
    import { formatNumber } from '../utils/utils';

    Chart.register(zoomPlugin);

    var startAmount = formatNumber("10000");
    var monthlyContribution = formatNumber("1000");
    function getStartAmountValue(): number {return Number(startAmount.replace(/,/g, ''));}
    function getMonthlyContributionValue(): number {return Number(monthlyContribution.replace(/,/g, ''));}

    const futureYears = 20;
    var futureMonths = 1 + 12*futureYears; // number of years
    const taxRate = 37.84 / 100;  //https://www.skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/aksjer-og-verdipapirer/om/aksjesparekonto-ask/

    var showAddFundInput = false;
    var showAddBankInput = false;

    /* data */
    var fundsData: FundResult[];
    var banksData: Bank[];

    /* reactive data */
    var funds: FundResult[] = [];
    var banks: Bank[] = [];
    var chart: Chart;


    function addFund(event: CustomEvent) {
        const option: AutocompleteOption = event.detail.option;
        funds.push(fundsData[option.index]);
        funds = funds; // Trigger reactivity
        
        showAddFundInput = false;
        plotGraph();
    }

    function addBank(event: CustomEvent) {
        const option: AutocompleteOption = event.detail.option;
        banks.push(banksData[option.index]);
        banks = banks; // Trigger reactivity
        
        showAddBankInput = false;
        plotGraph();
    }

    let inputElement: HTMLInputElement; // focus on input element on load
    $: if (showAddFundInput && inputElement) {
        inputElement.focus();
    }


    function calculateFund(fund: FundResult): {after_interest_after_fee: number, fee: number, after_tax: number}[]{
        let fundCalculations: {after_interest_after_fee: number, fee: number, after_tax: number}[] = [];
        fundCalculations.push({after_interest_after_fee: getStartAmountValue(), fee: 0, after_tax: getStartAmountValue()});

        const fee = fund.fund_info.fund_calculated_fee / (100*12); // this fee is yearly & so is the interest
        const interest = fund.historical_returns_info.yield_1y / (100*12);

        for (let i = 1; i < futureMonths; i++) 
        {
            let after_interest = fundCalculations[i-1].after_interest_after_fee * (1+interest);
            let fee_cost = after_interest * fee;
            let after_interest_after_fee = after_interest - fee_cost + getMonthlyContributionValue();

            let profit = after_interest_after_fee - (getStartAmountValue() + getMonthlyContributionValue() * i);
            let after_tax = (getStartAmountValue() + getMonthlyContributionValue() * i) + profit * (1-taxRate);
            fundCalculations.push({after_interest_after_fee: after_interest_after_fee, fee: fee_cost, after_tax: after_tax});
        }

        return fundCalculations;
    }


    function calculateBank(bank: Bank, months: number): number {
        /* months starts at 0 */
        if (months == 0) {
            return getStartAmountValue();
        }
        // recursive calculation of the bank's interest
        return calculateBank(bank, months-1) * (1 + (Number(bank.rentesats1)/(100*12))) + getMonthlyContributionValue();
    }

      function plotGraph() {
        if (chart) chart.destroy();

        const labels = Array.from({length: futureMonths}, (_, i) => {
            const date = new Date();
            date.setMonth(date.getMonth() + i);
            return date.toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });
        });

        const fundDatasets = funds.map((fund) => {
            return {
                label: fund.instrument_info.name,
                data: calculateFund(fund).map(calc => calc.after_tax),
                fill: false,
                tension: 0.1
            }
        });

        const bankDatasets = banks.map((bank) => {
            return {
                label: bank.leverandorVisningsnavn,
                data: Array.from({length: futureMonths}, (_, i) => calculateBank(bank, i)),
                fill: false,
                tension: 0.1
            }
        });

        chart = new Chart(
            document.getElementById('chart') as HTMLCanvasElement,
            {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [...fundDatasets, ...bankDatasets]
                },
                options: {
                    responsive: true,
                    plugins: {
                        zoom: {
                            zoom: {
                                wheel: { enabled: true },
                                pinch: { enabled: true },
                                mode: 'x',
                            }
                        }
                    }
                }
            }
        );

        chart.zoomScale('x', {min: 0, max: 50}, "zoom");
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
            console.log(fundsData[0]);
            funds = fundsData.filter(x => x.instrument_info.name.toLowerCase().includes('dnb global indeks'));
            banks = [banksData.filter(bank => bank.leverandorVisningsnavn.toLowerCase().includes('dnb'))[0]];

            plotGraph();
        } catch (error) {
            console.error('Error fetching stock price data:', error);
        }
    });
</script>

<main style="display: flex; flex-direction: column; align-items: center; height: 100vh; width: 95vw; gap: 0.5em;">
    <h1 style="display: flex; align-items: center; justify-content: center;">
        <span>Funds</span>
        <span style="font-size: 5rem; margin: 0 1rem 0 1rem;">VS</span>
        <span>Banks</span>
    </h1>

    <div style="display: flex; flex-direction: row;width: 100%;">
        <div style="display: flex; flex-direction: column; gap: 0.5em;width: 80%;">
            <canvas id="chart" ></canvas>
        </div>

        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5em;width: 20%;">
            <div>
                <label for="startAmount">Starting Amount:<br></label>
                <input type="text" id="startAmount" bind:value={startAmount} placeholder="Enter starting amount" on:input={(e) => {startAmount = formatNumber(e.currentTarget.value); plotGraph();}} />
            </div>
            <div>
                <label for="monthlyContribution">Monthly Contribution:</label>
                <input type="text" id="monthlyContribution" bind:value={monthlyContribution} placeholder="Enter monthly contribution" on:input={(e) => {monthlyContribution = formatNumber(e.currentTarget.value); plotGraph();}} />
            </div>
            <br>
            <div style="display: flex; flex-direction: row; gap: 0.5em;">
                <div style="display: flex; flex-direction: row; gap: 0.5em;">
                    <button style="display: flex; align-items: center; gap: 0.5em;white-space: nowrap;" on:click={() => {showAddFundInput = true; showAddBankInput = false;}} class="add-button">
                        <AddIcon /> Add Fund
                    </button>
                    <button style="display: flex; align-items: center; gap: 0.5em;white-space: nowrap;" on:click={() => {showAddBankInput = true; showAddFundInput = false;}} class="add-button">
                        <AddIcon /> Add Bank
                    </button>
                </div>
            </div>
            <div style="display: flex; flex-direction: row; gap: 0.5em;">
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
            </div>
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
                            <th colspan="3">
                                <div title={fund.instrument_info.name} style="display: flex; align-items: center; gap: 5px;">
                                    <img src={fund.instrument_info.instrument_icon_url} alt={fund.instrument_info.name} style="width: 20px; height: 20px;" />
                                    {fund.instrument_info.name}
                                </div>
                            </th>
                        {/each}
                        {#each banks as bank}
                            <th>
                                <div title={bank.leverandorVisningsnavn} style="display: flex; align-items: center; gap: 5px;">
                                    <img src={bank.icon_url} alt={bank.leverandorVisningsnavn} style="width: 20px; height: 20px;" />
                                    {bank.leverandorVisningsnavn}
                                </div>
                            </th>
                        {/each}
                    </tr>
                    <tr>
                        <th></th>
                        {#each funds as _}
                            <th>After Interest <br> & after fee</th>
                            <th>Fee</th>
                            <th>After Tax</th>
                        {/each}
                        {#each banks as _}
                            <th></th>
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
                            {#each funds.map(fund => calculateFund(fund)) as fundCalculation}
                                <td>{fundCalculation[index].after_interest_after_fee.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                                <td>{fundCalculation[index].fee.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                                <td>{fundCalculation[index].after_tax.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                            {/each}
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
</style>