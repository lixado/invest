<script lang="ts">
  import { onMount } from "svelte";
  import { fade } from 'svelte/transition';

  import { Chart } from "chart.js/auto";
  import zoomPlugin from "chartjs-plugin-zoom";

  import IconoirFileNotFound from "virtual:icons/iconoir/file-not-found";
  import LucideSidebarOpen from 'virtual:icons/lucide/sidebar-open';

  import type { FundResult, Bank, AutocompleteOption } from "./utils/models";
  import CardViewer from "./components/CardViewer.svelte";
  import SideBar from "./components/SideBar.svelte";

  Chart.register(zoomPlugin);

  var startAmount = 10000;
  var monthlyContribution = 1000;

  const futureYears = 20;
  var futureMonths = 1 + 12 * futureYears; // number of years
  const taxRate = 37.84 / 100; //https://www.skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/aksjer-og-verdipapirer/om/aksjesparekonto-ask/

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

  function calculateFund(
    fund: FundResult,
  ): { after_interest_after_fee: number; fee: number; after_tax: number }[] {
    let fundCalculations: {
      after_interest_after_fee: number;
      fee: number;
      after_tax: number;
    }[] = [];
    fundCalculations.push({
      after_interest_after_fee: startAmount,
      fee: 0,
      after_tax: startAmount,
    });

    const fee = fund.fund_info.fund_calculated_fee / (100 * 12); // this fee is yearly & so is the interest
    const interest = fund.historical_returns_info.yield_5y / (100 * 12 * 5);

    for (let i = 1; i < futureMonths; i++) {
      let after_interest =
        fundCalculations[i - 1].after_interest_after_fee * (1 + interest);
      let fee_cost = after_interest * fee;
      let after_interest_after_fee =
        after_interest - fee_cost + monthlyContribution;

      let profit =
        after_interest_after_fee -
        (startAmount + monthlyContribution * i);
      let after_tax =
        startAmount +
        monthlyContribution * i +
        profit * (1 - taxRate);

      fundCalculations.push({
        after_interest_after_fee: after_interest_after_fee,
        fee: fee_cost,
        after_tax: after_tax,
      });
    }

    return fundCalculations;
  }

  function calculateBank(bank: Bank, months: number): number {
    /* months starts at 0 */
    if (months == 0) {
      return startAmount;
    }
    // recursive calculation of the bank's interest
    return (
      calculateBank(bank, months - 1) *
        (1 + Number(bank.rentesats1) / (100 * 12)) +
      monthlyContribution
    );
  }

  function plotGraph() {
    if (chart) chart.destroy();

    const labels = Array.from({ length: futureMonths }, (_, i) => {
      const date = new Date();
      date.setMonth(date.getMonth() + i);
      return date.toLocaleDateString("en-GB", {
        month: "short",
        year: "numeric",
      });
    });

    const fundDatasets = funds.map((fund) => {
      return {
        label: fund.instrument_info.name,
        data: calculateFund(fund).map((calc) => calc.after_tax),
        fill: false,
        tension: 0.1,
      };
    });

    const bankDatasets = banks.map((bank) => {
      return {
        label: bank.leverandorVisningsnavn,
        data: Array.from({ length: futureMonths }, (_, i) =>
          calculateBank(bank, i),
        ),
        fill: false,
        tension: 0.1,
      };
    });

    const canvas = document.getElementById("chart") as HTMLCanvasElement;
    chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: labels,
        datasets: [...fundDatasets, ...bankDatasets],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true, // show legend
            title: {
              display: true,
              text: "*Fund numbers are after fees and after taxes, see table below for details",
            },
          },
          zoom: {
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              mode: "x",
            },
          },
        },
      },
    });

    chart.zoomScale("x", { min: 0, max: 50 }, "zoom");
  }

  var sidebarOpen: boolean = false;
  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }

  onMount(async () => {
    try {
      // get current url
      const currentUrl = window.location.href;

      // Read JSON from funds.json
      const fundsResponse = await fetch(currentUrl + "/funds.json");
      fundsData = await fundsResponse.json();

      // Read JSON from banks.json
      const banksResponse = await fetch(currentUrl + "/banks.json");
      banksData = await banksResponse.json();

      // Get up to 3 funds
      funds = fundsData
        .filter(
          (x) =>
            x.instrument_info.name.toLowerCase() ==
              "DNB Global Indeks A".toLocaleLowerCase() ||
            x.instrument_info.name.toLowerCase() ==
              "KLP AksjeNorge Aktiv P".toLocaleLowerCase() ||
            x.instrument_info.name.toLowerCase() ==
              "KLP AksjeUSA Indeks Valutasikret P".toLocaleLowerCase(),
        )
        .slice(0, 3);

      banks = banksData
        .filter((bank) =>
          bank.leverandorVisningsnavn.toLowerCase().includes("dnb"),
        )
        .slice(0, 3);

      plotGraph();
    } catch (error) {
      console.error("Error fetching stock price data:", error);
    }
  });
</script>

<main>
  {#if sidebarOpen}
    <SideBar on:resetZoom={e => {chart.resetZoom();}} on:close={toggleSidebar} bind:startAmount={startAmount} bind:monthlyContribution={monthlyContribution} on:change={plotGraph} />
  {:else}
    <button transition:fade={{ duration: 300 }} class="sidebar-button" on:click={toggleSidebar}><LucideSidebarOpen /></button>
  {/if}

  <div
    style="display: flex; flex-direction: column; align-items: center; height: 100vh; width: 95vw;"
  >
    <h1 class="title">
      <span>Funds</span>
      <span class="vs-text">VS</span>
      <span>Banks</span>
    </h1>

    <div class="chart-container" style="position: relative;">
      <canvas id="chart" class="custom-canvas"></canvas>
    </div>

    <br />

    <div
      style="display: flex; flex-direction: row; align-items: center;width: 100%;"
    >
      <!--         <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5em;width: 20%;">
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
      </div> -->
    </div>

    <div
      style="display: flex; flex-wrap: wrap; justify-content: center; width: 100%; gap: 1em;"
    >
      <div
        style="display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5em; flex: 1;"
      >
        {#each funds as fund}
          <CardViewer {fund} />
        {/each}
      </div>
      <hr style="align-self: stretch; margin: 0 1em;" />
      <div
        style="display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5em; flex: 1;"
      >
        {#each banks as bank}
          <CardViewer {bank} />
        {/each}
      </div>
    </div>

    {#if funds.length > 0 && banks.length > 0}
      <h1 style="text-align: center;">Comparison</h1>
      <div
        style="display: flex; flex-direction: column; gap: 0.5em;width: 100%;min-width: 100%; overflow-x: auto; flex: 1 0 100%;"
      >
        <table>
          <thead>
            <tr>
              <th>Date</th>
              {#each funds as fund}
                <th colspan="3">
                  <div
                    title={fund.instrument_info.name}
                    style="display: flex; align-items: center; gap: 5px;"
                  >
                    <img
                      src={fund.instrument_info.instrument_icon_url}
                      alt={fund.instrument_info.name}
                      style="width: 20px; height: 20px;"
                    />
                    {fund.instrument_info.name}
                  </div>
                </th>
              {/each}
              {#each banks as bank}
                <th>
                  <div
                    title={bank.leverandorVisningsnavn}
                    style="display: flex; align-items: center; gap: 5px;"
                  >
                    {#if bank.icon_url}
                      <img
                        src={bank.icon_url}
                        alt={bank.leverandorVisningsnavn}
                        style="width: 20px; height: 20px;"
                        on:error={() => {
                          bank.icon_url = "";
                        }}
                      />
                    {:else}
                      <IconoirFileNotFound style="width: 20px; height: 20px;" />
                    {/if}
                    {bank.leverandorVisningsnavn + ` (${bank.navn})`}
                  </div>
                </th>
              {/each}
            </tr>
            <tr>
              <th></th>
              {#each funds as _}
                <th>After Interest <br /> & after fee</th>
                <th>Fee</th>
                <th>After Tax</th>
              {/each}
              {#each banks as _}
                <th></th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each Array(futureMonths)
              .fill(0)
              .map((_, i) => {
                const date = new Date();
                date.setMonth(date.getMonth() + i);
                return date;
              }) as date, index}
              <tr>
                <td
                  >{date
                    .toLocaleDateString("en-GB", {
                      day: "2-digit",
                      month: "short",
                      year: "numeric",
                    })
                    .replace(/ /g, " ")}
                </td>
                {#each funds.map( (fund) => calculateFund(fund), ) as fundCalculation}
                  <td>
                    {fundCalculation[
                      index
                    ].after_interest_after_fee.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </td>
                  <td>
                    {fundCalculation[index].fee.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </td>
                  <td>
                    {fundCalculation[index].after_tax.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </td>
                {/each}
                {#each banks as bank}
                  <td>
                    {calculateBank(bank, index).toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</main>

<style>
  .sidebar-button {
    position: fixed;
    top: 50%;
    left: 10px;
    transform: translateY(-50%);
    z-index: 1000;
    display: flex;
    align-items: end;
    justify-content: end;
  }

  .chart-container {
    width: 95vw;
  }

  .custom-canvas {
    height: 82vh;
  }

  .title {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .vs-text {
    font-size: 5rem;
    margin: 0 1rem;
  }

  @media (max-width: 768px) {
    .title {
      font-size: 3rem;
    }

    .vs-text {
      font-size: 3rem; /* Adjust as needed */
    }
  }
</style>
