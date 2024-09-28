<script lang="ts">
	import { onMount } from "svelte";
	import { fade } from "svelte/transition";

	import { Chart } from "chart.js/auto";
	import zoomPlugin from "chartjs-plugin-zoom";

	import IconoirFileNotFound from "virtual:icons/iconoir/file-not-found";
	import LucideSidebarOpen from "virtual:icons/lucide/sidebar-open";
	import HelpIcon from "virtual:icons/lucide/help-circle";

	import type { FundResult, Bank } from "./utils/models";
	import CardViewer from "./components/CardViewer.svelte";
	import SideBar from "./components/SideBar.svelte";
	import { formatCurrency } from "./utils/utils";

	Chart.register(zoomPlugin);

	var IsMobile = window.innerWidth < 768;

	var startAmount = 10000;
	var monthlyContribution = 1000;

	const futureYears = 20;
	var futureMonths = 1 + 12 * futureYears; // number of years
	const taxRate = 37.84 / 100; //https://www.skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/aksjer-og-verdipapirer/om/aksjesparekonto-ask/

	/* data */
	var fundsData: FundResult[];
	var banksData: Bank[];

	/* reactive data */
	var funds: FundResult[] = [];
	var banks: Bank[] = [];

	function calculateFund(
		fund: FundResult,
	): {
		after_interest_after_fee: number;
		fee: number;
		tax: number;
		after_tax: number;
	}[] {
		let fundCalculations: {
			after_interest_after_fee: number;
			fee: number;
			tax: number;
			after_tax: number;
		}[] = [];
		fundCalculations.push({
			after_interest_after_fee: startAmount,
			fee: 0,
			tax: 0,
			after_tax: startAmount,
		});

		const fee = fund.fund_info.fund_calculated_fee / (100 * 12); // this fee is yearly & so is the interest
		const interest = fund.historical_returns_info.yield_5y ? fund.historical_returns_info.yield_5y / (100 * 12 * 5) : fund.historical_returns_info.yield_1y / (100 * 12 * 1);

		for (let i = 1; i < futureMonths; i++) {
			let after_interest =
				fundCalculations[i - 1].after_interest_after_fee *
				(1 + interest);
			let fee_cost = after_interest * fee;
			let after_interest_after_fee =
				after_interest - fee_cost + monthlyContribution;

			let profit =
				after_interest_after_fee -
				(startAmount + monthlyContribution * i);
			let tax = profit * taxRate;
			let after_tax =
				startAmount + monthlyContribution * i + (profit - tax);

			fundCalculations.push({
				after_interest_after_fee: after_interest_after_fee,
				fee: fee_cost,
				tax: tax,
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

	var chart: Chart;
	var selectedLegendItemIndex: number | null = null;
	var position: { x: number; y: number } | null = null;

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
				label: bank.leverandorVisningsnavn + ` (${bank.navn})`,
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
				interaction: {
					mode: 'nearest',
					axis: 'x',
					intersect: false,
				},
				plugins: {
					tooltip: {
						callbacks: {
							label: function (context) {
								let label = context.dataset.label || "";

								if (label) {
									label += ": ";
								}
								if (context.parsed.y !== null) {
									label += formatCurrency(context.parsed.y);
								}

								const monthCount = context.parsed.x;
								const totalSaved =
									monthCount * monthlyContribution +
									startAmount;
								const profit = context.parsed.y - totalSaved;

								return [
									label,
									`Saved: ${formatCurrency(totalSaved)}`,
									`Profit:   ${formatCurrency(profit)}`,
								];
							},
						},
					},
					legend: {
						display: true, // show legend
						title: {
							display: true,
							text: "*Fund numbers are after fees and after taxes, see table below for details",
						},
						onClick(e, legendItem, legend) {
							console.log(legendItem.datasetIndex);
							if (legendItem.datasetIndex === undefined) return;

							if (legendItem.datasetIndex >= funds.length) 
							{
								banks = banks.filter((_, index) => index !== legendItem.datasetIndex);
								plotGraph();
							}else{
								funds = funds.filter((_, index) => index !== legendItem.datasetIndex);
								plotGraph();
							}
						},
						onHover: function (event, legendItem, legend) {
							if(IsMobile) return;

							selectedLegendItemIndex =
								legendItem.datasetIndex ?? null;
							selectedLegendItemIndex =
								legendItem.datasetIndex ?? null;
							position =
								event.x != null && event.y != null
									? { x: event.x, y: event.y }
									: null;
						},
						onLeave: function (event, legendItem, legend) {
							selectedLegendItemIndex = null;
							position = null;
						},
					},
					zoom: {
						zoom: {
							wheel: { enabled: true },
							pinch: { enabled: !IsMobile },
							drag: { enabled: true },
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
							"KLP AksjeUSA Indeks Valutasikret P".toLocaleLowerCase(),
				)
				.slice(0, 3);

			banks = banksData
				.filter((bank) =>
					bank.leverandorVisningsnavn.toLowerCase().includes("dnb"),
				)
				.slice(0, 2);

			plotGraph();
		} catch (error) {
			console.error("Error fetching stock price data:", error);
		}
	});
</script>

<main>
	{#if selectedLegendItemIndex !== null && position !== null}
		<div
			style="position: absolute; top: {200 +
				position.y}px; left: {position.x}px;z-index: 1000;"
		>
			{#if selectedLegendItemIndex >= funds.length}
				<CardViewer
					bank={banks[selectedLegendItemIndex - funds.length]}
				/>
			{:else}
				<CardViewer fund={funds[selectedLegendItemIndex]} />
			{/if}
		</div>
	{/if}

	{#if sidebarOpen}
		<SideBar
			on:resetZoom={(e) => {
				chart.zoomScale("x", { min: 0, max: 50 }, "zoom");
			}}
			on:close={toggleSidebar}
			bind:startAmount
			bind:monthlyContribution
			on:change={(e) => {
				plotGraph();
				funds = funds; // Trigger reactivity
				banks = banks; // Trigger reactivity
			}}
			bind:fundsData
			bind:banksData
			bind:funds
			bind:banks
		/>
	{:else}
		<button
			transition:fade={{ duration: 300 }}
			class="sidebar-button"
			on:click={toggleSidebar}><LucideSidebarOpen /></button
		>
	{/if}

	<div class="main-container">
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

			<div class="table-container">
				<table style="max-width: fit-content;">
					<thead>
						<tr>
							<th class="sticky-header">Date</th>
							{#each funds as fund}
								<th colspan="4" class="sticky-header">
									<div
										title={fund.instrument_info.name}
										style="display: flex; align-items: center; gap: 5px;"
									>
										<img
											src={fund.instrument_info
												.instrument_icon_url}
											alt={fund.instrument_info.name}
											style="width: 20px; height: 20px;"
										/>
										{fund.instrument_info.name}
									</div>
								</th>
							{/each}
							{#each banks as bank}
								<th class="sticky-header">
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
											<IconoirFileNotFound
												style="width: 20px; height: 20px;"
											/>
										{/if}
										{bank.leverandorVisningsnavn +
											` (${bank.navn})`}
									</div>
								</th>
							{/each}
						</tr>
						<tr>
							<th class="sticky-header-2"></th>
							{#each funds as _}
								<th class="sticky-header-2">After interest &<br /> after fee</th>
								<th class="sticky-header-2">Fee</th>
								<th title="Tax is calculated as 37.84% of the profit, click on the icon to learn more" class="sticky-header-2">Tax 
									<a href="https://www.skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/aksjer-og-verdipapirer/om/aksjesparekonto-ask/" target="_blank"><HelpIcon /></a>
								</th>
								<th class="sticky-header-2">After Tax & <br /> after fees</th>
							{/each}
							{#each banks as _}
								<th class="sticky-header-2"></th>
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
										].after_interest_after_fee.toLocaleString(
											"en-US",
											{
												minimumFractionDigits: 2,
												maximumFractionDigits: 2,
											},
										)}
									</td>
									<td>
										{fundCalculation[
											index
										].fee.toLocaleString("en-US", {
											minimumFractionDigits: 2,
											maximumFractionDigits: 2,
										})}
									</td>
									<td>
										{fundCalculation[
											index
										].tax.toLocaleString("en-US", {
											minimumFractionDigits: 2,
											maximumFractionDigits: 2,
										})}
									</td>
									<td>
										{fundCalculation[
											index
										].after_tax.toLocaleString("en-US", {
											minimumFractionDigits: 2,
											maximumFractionDigits: 2,
										})}
									</td>
								{/each}
								{#each banks as bank}
									<td>
										{calculateBank(
											bank,
											index,
										).toLocaleString("en-US", {
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

<svelte:window on:scroll={(e) => {
	if (window.scrollY > 0) {
		sidebarOpen = false;
	}
}}/>

<style>
	.main-container {
		display: flex; 
		flex-direction: column; 
		align-items: center; 
		height: 100vh; 
		width: 95vw;
	}

	.sidebar-button {
		position: fixed;
		top: 50vh;
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

	.table-container {
		max-height: 70vh;
		position: relative;
	}

	table {
		border-collapse: collapse;
		width: 100%;
	}

	.sticky-header {
		position: sticky;
		top: 0;
		z-index: 10;
	}

	.sticky-header-2 {
		position: sticky;
		top: 39px;
		z-index: 10;
	}

	th, td {
		padding: 8px;
		text-align: left;
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
