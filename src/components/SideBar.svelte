<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { formatNumber } from "../utils/utils";

	import LucideX from "virtual:icons/lucide/x";
	import PhTrash from "virtual:icons/ph/trash";
	import AddIcon from "virtual:icons/lucide/plus";
	import LucideRotateCcw from "virtual:icons/lucide/rotate-ccw";
	import AutocompleteSelector from "./AutocompleteSelector.svelte";
	import type { AutocompleteOption, Bank, FundResult } from "../utils/models";


	const dispatch = createEventDispatcher();

	export let startAmount: number = 10000;
	export let monthlyContribution: number = 1000;
	export let startDateInput: string = "";
	export let minStartDate: string = "";
	export let maxStartDate: string = "";
	export let fundsData: FundResult[] = [];
	export let banksData: Bank[] = [];
	export let funds: FundResult[] = [];
	export let banks: Bank[] = [];

	let startAmountInput: string = formatNumber(startAmount.toString());
	let monthlyContributionInput: string = formatNumber(
		monthlyContribution.toString(),
	);

	let showAddFundInput = false;
	let showAddBankInput = false;

	function addFund(event: CustomEvent) {
		const option: AutocompleteOption = event.detail.option;
		funds = [...funds, fundsData[option.index]];
		showAddFundInput = false;
		dispatch("change");
	}

	function addBank(event: CustomEvent) {
		const option: AutocompleteOption = event.detail.option;
		banks = [...banks, banksData[option.index]];
		showAddBankInput = false;
		dispatch("change");
	}

	function change() {
		startAmount = Number(startAmountInput.replace(/,/g, ""));
		monthlyContribution = Number(monthlyContributionInput.replace(/,/g, ""));
		dispatch("change");
	}

	function clearAll() {
		funds = [];
		banks = [];
		dispatch("change");
	}
</script>

<aside class="sidebar glass">
	<div class="head">
		<div>
			<p class="eyebrow">Controls</p>
			<h2>Compare</h2>
		</div>
		<button class="btn btnIcon btnGhost" type="button" on:click={() => dispatch("close")} aria-label="Close menu">
			<LucideX />
		</button>
	</div>

	<div class="content">
		<button
			class="btn"
			type="button"
			on:click={() => {
				dispatch("resetZoom");
			}}
		>
			<LucideRotateCcw /> Reset zoom
		</button>

		<div class="field">
			<label for="startDate">Start date</label>
			<input
				id="startDate"
				type="date"
				bind:value={startDateInput}
				min={minStartDate || undefined}
				max={maxStartDate || undefined}
				on:change={() => dispatch("change")}
			/>
			<p class="hint">Backtest from this date to today using real fund returns.</p>
		</div>

		<div class="field">
			<label for="startAmount">Start amount</label>
			<input
				id="startAmount"
				type="text"
				bind:value={startAmountInput}
				placeholder="10,000"
				on:input={(e) => {
					startAmountInput = formatNumber(e.currentTarget.value);
					change();
				}}
			/>
		</div>

		<div class="field">
			<label for="monthlyContribution">Monthly contribution</label>
			<input
				id="monthlyContribution"
				type="text"
				bind:value={monthlyContributionInput}
				placeholder="1,000"
				on:input={(e) => {
					monthlyContributionInput = formatNumber(e.currentTarget.value);
					change();
				}}
			/>
		</div>

		<section class="section">
			<div class="sectionHead">
				<h3>Funds</h3>
				<span>{funds.length}</span>
			</div>
			{#if showAddFundInput}
				<AutocompleteSelector
					placeholder="Search funds…"
					options={fundsData.map((fund, index) => ({
						index,
						name: fund.instrument_info.name,
						icon_url: fund.instrument_info.instrument_icon_url,
						interest_rate: fund.annual_growth_info.annual_growth_1y,
					}))}
					on:select={addFund}
				/>
			{:else}
				<button class="btn btnPrimary" type="button" on:click={() => (showAddFundInput = true)}>
					<AddIcon /> Add fund
				</button>
			{/if}
		</section>

		<section class="section">
			<div class="sectionHead">
				<h3>Banks</h3>
				<span>{banks.length}</span>
			</div>
			{#if showAddBankInput}
				<AutocompleteSelector
					placeholder="Search banks…"
					options={banksData.map((bank, index) => ({
						index,
						name: bank.leverandorVisningsnavn + ` (${bank.navn})`,
						icon_url:
							bank.icon_url ||
							(bank.leverandorUrl.endsWith("/")
								? bank.leverandorUrl + "favicon.ico"
								: bank.leverandorUrl + "/favicon.ico"),
						interest_rate: Number(bank.rentesats1),
					}))}
					on:select={addBank}
				/>
			{:else}
				<button class="btn btnPrimary" type="button" on:click={() => (showAddBankInput = true)}>
					<AddIcon /> Add bank
				</button>
			{/if}
		</section>

		{#if funds.length > 0 || banks.length > 0}
			<button class="btn" type="button" on:click={clearAll}>
				<PhTrash /> Clear all
			</button>
		{/if}
	</div>
</aside>

<style>
	.sidebar {
		position: fixed;
		left: 16px;
		top: 16px;
		bottom: 16px;
		width: min(320px, calc(100vw - 32px));
		border-radius: 24px;
		z-index: 1000;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		animation: panelIn 0.28s ease both;
	}

	.head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
		padding: 18px 18px 8px;
		text-align: left;
	}

	.eyebrow {
		margin: 0;
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--text);
	}

	h2 {
		margin: 2px 0 0;
		font-size: 1.35rem;
		font-weight: 750;
	}

	.content {
		display: flex;
		flex-direction: column;
		gap: 14px;
		padding: 8px 18px 18px;
		overflow: auto;
	}

	.section {
		display: flex;
		flex-direction: column;
		gap: 10px;
		padding: 12px;
		border-radius: 16px;
		background: var(--glass-bg-nested);
		border: 1px solid var(--glass-border-nested);
	}

	.sectionHead {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.sectionHead h3 {
		margin: 0;
		font-size: 0.95rem;
	}

	.sectionHead span {
		font-size: 12px;
		font-weight: 700;
		color: var(--text);
		background: rgba(255, 255, 255, 0.5);
		border-radius: 999px;
		padding: 2px 8px;
	}

	.hint {
		margin: 0;
		font-size: 11px;
		font-weight: 600;
		color: var(--text);
		line-height: 1.35;
	}

	input[type="date"] {
		text-align: left;
	}

	@media (max-width: 768px) {
		.sidebar {
			left: 10px;
			right: 10px;
			width: auto;
			bottom: auto;
			max-height: min(85vh, 720px);
		}
	}
</style>
