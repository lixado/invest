<script lang="ts">
	import { onMount } from "svelte";
	import { slide } from "svelte/transition";

	import { Chart } from "chart.js/auto";
	import zoomPlugin from "chartjs-plugin-zoom";

	import IconoirFileNotFound from "virtual:icons/iconoir/file-not-found";
	import LucideMenu from "virtual:icons/lucide/menu";
	import HelpIcon from "virtual:icons/lucide/help-circle";
	import LucideChevronDown from "virtual:icons/lucide/chevron-down";
	import LucideChevronUp from "virtual:icons/lucide/chevron-up";

	import type { BacktestPoint, Bank, FundHistory, FundResult } from "./utils/models";
	import CardViewer from "./components/CardViewer.svelte";
	import SideBar from "./components/SideBar.svelte";
	import { formatCurrency } from "./utils/utils";
	import {
		backtestBank,
		backtestFund,
		earliestHistoryDate,
		monthEndsBetween,
		toInputDate,
	} from "./utils/backtest";

	Chart.register(zoomPlugin);

	const IsMobile = window.innerWidth < 768;

	let startAmount = 10000;
	let monthlyContribution = 1000;
	let startDateInput = "";
	let minStartDate = "";
	let maxStartDate = toInputDate(new Date());

	let fundsData: FundResult[] = [];
	let banksData: Bank[] = [];
	let funds: FundResult[] = [];
	let banks: Bank[] = [];
	let historyById: Record<string, FundHistory> = {};
	let historyMissing: string[] = [];

	let loading = true;
	let historyLoading = false;
	let loadError = "";
	let showDetails = false;
	let showAfterTax = true;
	let dataUpdatedLabel = "";

	let chart: Chart;
	let selectedLegendItemIndex: number | null = null;
	let position: { x: number; y: number } | null = null;
	let sidebarOpen = !IsMobile;

	function fundHistoryId(fund: FundResult): string {
		return fund.instrument_info.market_data_order_book_id || "";
	}

	function getFundHistory(fund: FundResult): FundHistory | null {
		const id = fundHistoryId(fund);
		return id ? historyById[id] || null : null;
	}

	async function loadHistories(selected: FundResult[]) {
		const base = import.meta.env.BASE_URL;
		historyLoading = true;
		const missing: string[] = [];
		const next: Record<string, FundHistory> = { ...historyById };

		await Promise.all(
			selected.map(async (fund) => {
				const id = fundHistoryId(fund);
				if (!id) {
					missing.push(fund.instrument_info.name);
					return;
				}
				if (next[id]) return;
				try {
					const res = await fetch(`${base}history/${id}.json`);
					if (!res.ok) {
						missing.push(fund.instrument_info.name);
						return;
					}
					next[id] = await res.json();
				} catch {
					missing.push(fund.instrument_info.name);
				}
			}),
		);

		historyById = next;
		historyMissing = missing;

		const available = selected
			.map(getFundHistory)
			.filter((h): h is FundHistory => !!h);
		const earliest = earliestHistoryDate(available);
		if (earliest) {
			minStartDate = toInputDate(earliest);
			// Default to the oldest available history date.
			if (!startDateInput || new Date(startDateInput) < earliest) {
				startDateInput = toInputDate(earliest);
			}
		}

		historyLoading = false;
	}

	function fundSeries(fund: FundResult): BacktestPoint[] {
		const history = getFundHistory(fund);
		if (!history || !startDateInput) return [];
		return backtestFund(
			history,
			new Date(startDateInput),
			new Date(),
			startAmount,
			monthlyContribution,
			fund.fund_info.fund_calculated_fee || 0,
		);
	}

	function bankSeries(bank: Bank): BacktestPoint[] {
		if (!startDateInput) return [];
		const months = monthEndsBetween(new Date(startDateInput), new Date());
		return backtestBank(
			months,
			startAmount,
			monthlyContribution,
			Number(bank.rentesats1) || 0,
		);
	}

	function plotGraph() {
		const canvas = document.getElementById("chart") as HTMLCanvasElement;
		if (!canvas) return;
		if (chart) chart.destroy();

		const fundResults = funds.map((fund) => ({
			fund,
			series: fundSeries(fund),
		}));
		const bankResults = banks.map((bank) => ({
			bank,
			series: bankSeries(bank),
		}));

		const labelSource =
			fundResults.find((f) => f.series.length)?.series ||
			bankResults.find((b) => b.series.length)?.series ||
			[];

		const labels = labelSource.map((p) =>
			p.date.toLocaleDateString("en-GB", {
				month: "short",
				year: "numeric",
			}),
		);

		const fundDatasets = fundResults.map(({ fund, series }) => ({
			label: fund.instrument_info.name,
			data: series.map((p) => (showAfterTax ? p.afterTax : p.value)),
			fill: false,
			tension: 0.15,
			borderWidth: 2.5,
			pointRadius: 0,
			pointHoverRadius: 4,
		}));

		const bankDatasets = bankResults.map(({ bank, series }) => ({
			label: bank.leverandorVisningsnavn + ` (${bank.navn})`,
			data: series.map((p) => p.value),
			fill: false,
			tension: 0.15,
			borderWidth: 2.5,
			pointRadius: 0,
			pointHoverRadius: 4,
			borderDash: [6, 4],
		}));

		chart = new Chart(canvas, {
			type: "line",
			data: {
				labels,
				datasets: [...fundDatasets, ...bankDatasets],
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				interaction: {
					mode: "nearest",
					axis: "x",
					intersect: false,
				},
				scales: {
					x: {
						grid: { color: "rgba(15, 23, 42, 0.06)" },
						ticks: { color: "rgba(15, 23, 42, 0.55)", maxTicksLimit: 10 },
					},
					y: {
						grid: { color: "rgba(15, 23, 42, 0.06)" },
						ticks: {
							color: "rgba(15, 23, 42, 0.55)",
							callback: (value) =>
								typeof value === "number" ? formatCurrency(value) : value,
						},
					},
				},
				plugins: {
					tooltip: {
						backgroundColor: "rgba(255, 255, 255, 0.92)",
						titleColor: "#0f172a",
						bodyColor: "#0f172a",
						borderColor: "rgba(255, 255, 255, 0.7)",
						borderWidth: 1,
						callbacks: {
							label(context) {
								const idx = context.dataIndex;
								const isBank = (context.datasetIndex ?? 0) >= funds.length;
								const series = isBank
									? bankResults[(context.datasetIndex ?? 0) - funds.length]
											?.series
									: fundResults[context.datasetIndex ?? 0]?.series;
								const point = series?.[idx];
								const label = context.dataset.label || "";
								if (!point) {
									return `${label}: ${formatCurrency(context.parsed.y)}`;
								}
								const plotted = isBank
									? point.value
									: showAfterTax
										? point.afterTax
										: point.value;
								return [
									`${label}: ${formatCurrency(plotted)}`,
									`Contributed: ${formatCurrency(point.contributed)}`,
									`Profit: ${formatCurrency(point.value - point.contributed)}`,
									...(isBank || !showAfterTax
										? []
										: [`After fees: ${formatCurrency(point.value)}`]),
								];
							},
						},
					},
					legend: {
						display: true,
						labels: {
							color: "#0f172a",
							usePointStyle: true,
							padding: 16,
						},
						title: {
							display: true,
							color: "rgba(15, 23, 42, 0.55)",
							text: showAfterTax
								? "Historical path · funds after fees & illustrative ASK tax · click legend to remove"
								: "Historical path · funds after fees (before tax) · click legend to remove",
						},
						onClick(_e, legendItem) {
							if (legendItem.datasetIndex === undefined) return;
							const idx = legendItem.datasetIndex;
							if (idx >= funds.length) {
								banks = banks.filter((_, i) => i !== idx - funds.length);
							} else {
								funds = funds.filter((_, i) => i !== idx);
							}
							void refreshAndPlot();
						},
						onHover(event, legendItem) {
							if (IsMobile) return;
							selectedLegendItemIndex = legendItem.datasetIndex ?? null;
							position =
								event.x != null && event.y != null
									? { x: event.x, y: event.y }
									: null;
						},
						onLeave() {
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
	}

	async function refreshAndPlot() {
		await loadHistories(funds);
		plotGraph();
	}

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	onMount(async () => {
		try {
			const base = import.meta.env.BASE_URL;
			const [fundsResponse, banksResponse, metaResponse] = await Promise.all([
				fetch(`${base}funds.json`),
				fetch(`${base}banks.json`),
				fetch(`${base}data-meta.json`).catch(() => null),
			]);

			fundsData = await fundsResponse.json();
			banksData = await banksResponse.json();

			if (metaResponse && metaResponse.ok) {
				const meta = await metaResponse.json();
				dataUpdatedLabel = meta.updatedAt
					? new Date(meta.updatedAt).toLocaleDateString("en-GB", {
							day: "numeric",
							month: "short",
							year: "numeric",
						})
					: "";
			}

			funds = fundsData
				.filter(
					(x) =>
						x.instrument_info.name.toLowerCase() == "dnb global indeks a" ||
						x.instrument_info.name.toLowerCase() ==
							"klp aksjeusa indeks valutasikret n",
				)
				.slice(0, 3);

			banks = banksData
				.filter(
					(bank) =>
						bank.leverandorVisningsnavn.toLowerCase().includes("dnb") &&
						bank.navn.toLowerCase().includes("spare"),
				)
				.slice(0, 2);
			if (banks.length === 0) {
				banks = banksData
					.filter((bank) =>
						bank.leverandorVisningsnavn.toLowerCase().includes("dnb"),
					)
					.slice(0, 2);
			}

			loading = false;
			await refreshAndPlot();
		} catch (error) {
			loading = false;
			loadError = "Could not load fund/bank data.";
			console.error("Error fetching data:", error);
		}
	});

	$: fundCalcs = funds.map((fund) => fundSeries(fund));
	$: bankCalcs = banks.map((bank) => bankSeries(bank));
	$: detailMonths =
		fundCalcs.find((s) => s.length)?.map((p) => p.date) ||
		bankCalcs.find((s) => s.length)?.map((p) => p.date) ||
		[];
</script>

<main class="app">
	{#if selectedLegendItemIndex !== null && position !== null}
		<div
			class="hoverCard"
			style="top: {180 + position.y}px; left: {position.x}px;"
		>
			{#if selectedLegendItemIndex >= funds.length}
				<CardViewer bank={banks[selectedLegendItemIndex - funds.length]} />
			{:else}
				<CardViewer fund={funds[selectedLegendItemIndex]} />
			{/if}
		</div>
	{/if}

	<header class="topBar glass">
		<div class="brand">
			<button
				class="btn btnIcon btnGhost menuBtn"
				type="button"
				on:click={toggleSidebar}
				aria-label="Toggle menu"
			>
				<LucideMenu />
			</button>
			<div class="brandText">
				<h1>Funds <span>vs</span> Banks</h1>
				<p>
					Historical backtest
					{#if startDateInput}
						· from {new Date(startDateInput).toLocaleDateString("en-GB", {
							month: "short",
							year: "numeric",
						})}
					{/if}
					{#if dataUpdatedLabel}
						· data {dataUpdatedLabel}
					{/if}
				</p>
			</div>
		</div>
		<div class="status glassStrong">
			{funds.length} funds · {banks.length} banks
		</div>
	</header>

	{#if sidebarOpen}
		<SideBar
			on:resetZoom={() => {
				chart?.resetZoom?.();
			}}
			on:close={toggleSidebar}
			bind:startAmount
			bind:monthlyContribution
			bind:startDateInput
			{minStartDate}
			{maxStartDate}
			on:change={() => {
				void refreshAndPlot();
			}}
			bind:fundsData
			bind:banksData
			bind:funds
			bind:banks
		/>
	{/if}

	<section class="stage" class:withSidebar={sidebarOpen && !IsMobile}>
		{#if loading}
			<div class="state glass">
				<div class="loader"></div>
				<p>Loading markets…</p>
			</div>
		{:else if loadError}
			<div class="state glass">
				<p>{loadError}</p>
			</div>
		{:else}
			{#if historyMissing.length}
				<div class="notice glassStrong">
					Missing price history for: {historyMissing.join(", ")}. Run
					<code>npm run update:history</code> to download Nordnet series.
				</div>
			{/if}

			<div class="chartPanel glass">
				<div class="chartHead">
					<div>
						<h2>Historical growth</h2>
						<p>
							{#if historyLoading}
								Loading price history…
							{:else}
								Real ups & downs with monthly contributions · scroll/drag to zoom
							{/if}
						</p>
					</div>
					<label class="taxToggle" title="Show fund values after fees and illustrative ASK tax">
						<span>After tax</span>
						<input
							type="checkbox"
							role="switch"
							bind:checked={showAfterTax}
							on:change={() => plotGraph()}
						/>
						<span class="switch" aria-hidden="true"></span>
					</label>
				</div>
				<div class="chartWrap">
					<canvas id="chart"></canvas>
				</div>
			</div>

			<div class="cardsRow">
				<div class="cardGroup">
					{#each funds as fund}
						<CardViewer {fund} />
					{/each}
				</div>
				<div class="divider" aria-hidden="true"></div>
				<div class="cardGroup">
					{#each banks as bank}
						<CardViewer {bank} />
					{/each}
				</div>
			</div>

			{#if detailMonths.length > 0}
				<section class="detailsPanel glass">
					<button
						class="detailsToggle"
						type="button"
						on:click={() => (showDetails = !showDetails)}
						aria-expanded={showDetails}
					>
						<div>
							<h2>Month-by-month details</h2>
							<p>Portfolio value, fees, illustrative ASK tax, contributions</p>
						</div>
						<span class="btn btnPrimary">
							{#if showDetails}
								<LucideChevronUp /> Hide details
							{:else}
								<LucideChevronDown /> Show details
							{/if}
						</span>
					</button>

					{#if showDetails}
						<div class="tableWrap" transition:slide={{ duration: 220 }}>
							<table>
								<thead>
									<tr>
										<th class="sticky">Date</th>
										{#each funds as fund}
											<th colspan="4" class="sticky">
												<div class="thProduct" title={fund.instrument_info.name}>
													<img
														src={fund.instrument_info.instrument_icon_url}
														alt=""
													/>
													{fund.instrument_info.name}
												</div>
											</th>
										{/each}
										{#each banks as bank}
											<th class="sticky">
												<div
													class="thProduct"
													title={bank.leverandorVisningsnavn}
												>
													{#if bank.icon_url}
														<img
															src={bank.icon_url}
															alt=""
															on:error={() => {
																bank.icon_url = "";
															}}
														/>
													{:else}
														<IconoirFileNotFound />
													{/if}
													{bank.leverandorVisningsnavn + ` (${bank.navn})`}
												</div>
											</th>
										{/each}
									</tr>
									<tr>
										<th class="sticky2"></th>
										{#each funds as _}
											<th class="sticky2">Value</th>
											<th class="sticky2">Fee</th>
											<th class="sticky2" title="Illustrative 37.84% of profit">
												Tax
												<a
													href="https://www.skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/aksjer-og-verdipapirer/om/aksjesparekonto-ask/"
													target="_blank"
													rel="noopener noreferrer"
													aria-label="About ASK tax"
												>
													<HelpIcon />
												</a>
											</th>
											<th class="sticky2">After tax</th>
										{/each}
										{#each banks as _}
											<th class="sticky2">Balance</th>
										{/each}
									</tr>
								</thead>
								<tbody>
									{#each detailMonths as date, index}
										<tr>
											<td>
												{date.toLocaleDateString("en-GB", {
													day: "2-digit",
													month: "short",
													year: "numeric",
												})}
											</td>
											{#each fundCalcs as series}
												{#if series[index]}
													<td>
														{series[index].value.toLocaleString("en-US", {
															minimumFractionDigits: 2,
															maximumFractionDigits: 2,
														})}
													</td>
													<td>
														{series[index].fee.toLocaleString("en-US", {
															minimumFractionDigits: 2,
															maximumFractionDigits: 2,
														})}
													</td>
													<td>
														{series[index].tax.toLocaleString("en-US", {
															minimumFractionDigits: 2,
															maximumFractionDigits: 2,
														})}
													</td>
													<td>
														{series[index].afterTax.toLocaleString("en-US", {
															minimumFractionDigits: 2,
															maximumFractionDigits: 2,
														})}
													</td>
												{:else}
													<td colspan="4">—</td>
												{/if}
											{/each}
											{#each bankCalcs as series}
												<td>
													{#if series[index]}
														{series[index].value.toLocaleString("en-US", {
															minimumFractionDigits: 2,
															maximumFractionDigits: 2,
														})}
													{:else}
														—
													{/if}
												</td>
											{/each}
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{/if}
				</section>
			{/if}
		{/if}
	</section>
</main>

<svelte:window
	on:scroll={() => {
		if (IsMobile && window.scrollY > 0) sidebarOpen = false;
	}}
/>

<style>
	.app {
		min-height: 100vh;
		padding: 16px;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.topBar {
		position: sticky;
		top: 16px;
		z-index: 40;
		border-radius: 20px;
		padding: 12px 16px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		animation: riseIn 0.35s ease both;
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 12px;
		text-align: left;
	}

	.brandText h1 {
		margin: 0;
		font-size: clamp(1.25rem, 2.4vw, 1.7rem);
		font-weight: 780;
		letter-spacing: -0.02em;
	}

	.brandText h1 span {
		color: var(--accent);
		font-weight: 700;
	}

	.brandText p {
		margin: 2px 0 0;
		font-size: 12px;
		font-weight: 600;
		color: var(--text);
	}

	.status {
		border-radius: 999px;
		padding: 8px 12px;
		font-size: 12px;
		font-weight: 700;
		white-space: nowrap;
	}

	.stage {
		display: flex;
		flex-direction: column;
		gap: 16px;
		width: min(100%, 1400px);
		margin: 0 auto;
		transition: padding-left 0.25s ease;
	}

	.stage.withSidebar {
		padding-left: 340px;
	}

	.state {
		border-radius: 24px;
		min-height: 280px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 12px;
	}

	.notice {
		border-radius: 16px;
		padding: 12px 14px;
		text-align: left;
		font-size: 13px;
		font-weight: 600;
		color: var(--text-h);
	}

	.notice code {
		font-family: var(--mono);
		font-size: 12px;
	}

	.chartPanel {
		border-radius: 24px;
		padding: 16px;
		animation: riseIn 0.4s ease both;
	}

	.chartHead {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		margin-bottom: 8px;
		text-align: left;
	}

	.chartHead h2 {
		margin: 0;
		font-size: 1.1rem;
	}

	.chartHead p {
		margin: 4px 0 0;
		font-size: 12px;
		color: var(--text);
		font-weight: 600;
	}

	.taxToggle {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		cursor: pointer;
		user-select: none;
		flex-shrink: 0;
		font-size: 12px;
		font-weight: 700;
		color: var(--text-h);
		padding: 8px 10px;
		border-radius: 999px;
		background: var(--glass-bg-nested);
		border: 1px solid var(--glass-border-nested);
	}

	.taxToggle input {
		position: absolute;
		opacity: 0;
		width: 0;
		height: 0;
	}

	.taxToggle .switch {
		position: relative;
		width: 40px;
		height: 24px;
		border-radius: 999px;
		background: rgba(15, 23, 42, 0.18);
		box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.12);
		transition: background 0.2s ease;
	}

	.taxToggle .switch::after {
		content: "";
		position: absolute;
		top: 3px;
		left: 3px;
		width: 18px;
		height: 18px;
		border-radius: 50%;
		background: #fff;
		box-shadow: 0 1px 3px rgba(15, 23, 42, 0.25);
		transition: transform 0.2s ease;
	}

	.taxToggle input:checked + .switch {
		background: rgba(0, 122, 255, 0.55);
	}

	.taxToggle input:checked + .switch::after {
		transform: translateX(16px);
	}

	.taxToggle input:focus-visible + .switch {
		box-shadow: 0 0 0 3px var(--accent-soft);
	}

	.chartWrap {
		height: min(62vh, 640px);
		position: relative;
	}

	.cardsRow {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		align-items: stretch;
		gap: 12px;
	}

	.cardGroup {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 12px;
		flex: 1;
	}

	.divider {
		width: 1px;
		align-self: stretch;
		background: rgba(15, 23, 42, 0.12);
		min-height: 40px;
	}

	.detailsPanel {
		border-radius: 24px;
		padding: 8px;
		animation: riseIn 0.45s ease both;
	}

	.detailsToggle {
		width: 100%;
		appearance: none;
		border: 0;
		background: transparent;
		border-radius: 18px;
		padding: 14px 16px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		cursor: pointer;
		text-align: left;
		color: inherit;
		font: inherit;
	}

	.detailsToggle:hover {
		background: var(--glass-bg-nested);
	}

	.detailsToggle h2 {
		margin: 0;
		font-size: 1.05rem;
	}

	.detailsToggle p {
		margin: 4px 0 0;
		font-size: 12px;
		color: var(--text);
		font-weight: 600;
	}

	.tableWrap {
		max-height: 70vh;
		overflow: auto;
		border-radius: 18px;
		margin: 0 8px 8px;
		background: rgba(255, 255, 255, 0.35);
		border: 1px solid var(--glass-border-nested);
	}

	table {
		border-collapse: separate;
		border-spacing: 0;
		width: max-content;
		min-width: 100%;
		font-size: 13px;
		text-align: left;
	}

	th,
	td {
		padding: 10px 12px;
		border-bottom: 1px solid rgba(15, 23, 42, 0.06);
		white-space: nowrap;
	}

	th {
		background: rgba(255, 255, 255, 0.72);
		backdrop-filter: blur(10px);
		font-weight: 700;
	}

	.sticky {
		position: sticky;
		top: 0;
		z-index: 3;
	}

	.sticky2 {
		position: sticky;
		top: 42px;
		z-index: 2;
		font-size: 12px;
		color: var(--text);
	}

	.thProduct {
		display: flex;
		align-items: center;
		gap: 6px;
		max-width: 220px;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.thProduct img {
		width: 18px;
		height: 18px;
		border-radius: 4px;
	}

	tbody tr:hover {
		background: rgba(0, 122, 255, 0.05);
	}

	.hoverCard {
		position: absolute;
		z-index: 1000;
		pointer-events: none;
	}

	@media (max-width: 768px) {
		.app {
			padding: 10px;
		}

		.topBar {
			top: 10px;
		}

		.stage.withSidebar {
			padding-left: 0;
		}

		.status {
			display: none;
		}

		.divider {
			width: 100%;
			height: 1px;
		}

		.detailsToggle {
			flex-direction: column;
			align-items: stretch;
		}
	}
</style>
