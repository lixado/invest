<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import type { AutocompleteOption } from "../utils/models";

	export let options: AutocompleteOption[] = [];
	export let placeholder = "Search…";

	let inputValue = "";
	let filteredOptions: AutocompleteOption[] = [];
	const dispatch = createEventDispatcher();

	function handleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		inputValue = target.value;

		filteredOptions = options.filter((option) =>
			option.name?.toLowerCase().includes(inputValue.toLowerCase()),
		);

		if (filteredOptions.length === 1) {
			handleSelect(filteredOptions[0]);
		}
	}

	function handleSelect(option: AutocompleteOption) {
		dispatch("select", { option });
	}

	$: recommended = options
		.filter((option) => option.name?.toLowerCase().includes("dnb"))
		.sort(() => Math.random() - 0.5)
		.slice(0, 5);
</script>

<div class="wrap">
	<input
		type="search"
		{placeholder}
		bind:value={inputValue}
		on:input={handleInput}
		autocomplete="off"
	/>

	<ul class="list glass">
		{#if inputValue.length === 0}
			<li class="label">Recommended</li>
			{#each recommended as option}
				<li>
					<button type="button" on:click={() => handleSelect(option)}>
						{#if option.icon_url}
							<img
								src={option.icon_url}
								alt=""
								on:error={() => {
									option.icon_url = "";
								}}
							/>
						{/if}
						<span class="name">{option.name}</span>
						{#if option.interest_rate}
							<span class="rate">{option.interest_rate.toFixed(1)}%</span>
						{/if}
					</button>
				</li>
			{/each}
		{:else if filteredOptions.length === 0}
			<li class="label">No matches</li>
		{:else}
			{#each filteredOptions.slice(0, 40) as option}
				<li>
					<button type="button" on:click={() => handleSelect(option)}>
						{#if option.icon_url}
							<img
								src={option.icon_url}
								alt=""
								on:error={() => {
									option.icon_url = "";
								}}
							/>
						{/if}
						<span class="name">{option.name}</span>
						{#if option.interest_rate}
							<span class="rate">{option.interest_rate.toFixed(1)}%</span>
						{/if}
					</button>
				</li>
			{/each}
		{/if}
	</ul>
</div>

<style>
	.wrap {
		position: relative;
		width: min(100%, 320px);
	}

	input {
		width: 100%;
		border-radius: 12px;
		border: 1px solid var(--glass-border-nested);
		background: rgba(255, 255, 255, 0.6);
		color: var(--text-h);
		padding: 0.7rem 0.9rem;
		font: inherit;
		font-weight: 600;
	}

	input:focus {
		outline: none;
		border-color: rgba(0, 122, 255, 0.45);
		box-shadow: 0 0 0 3px var(--accent-soft);
	}

	.list {
		list-style: none;
		margin: 8px 0 0;
		padding: 6px;
		border-radius: 16px;
		max-height: 280px;
		overflow-y: auto;
		position: absolute;
		left: 0;
		right: 0;
		z-index: 20;
		text-align: left;
	}

	.label {
		padding: 8px 10px;
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--text);
	}

	button {
		width: 100%;
		appearance: none;
		border: 0;
		background: transparent;
		border-radius: 12px;
		min-height: 44px;
		padding: 8px 10px;
		display: flex;
		align-items: center;
		gap: 8px;
		cursor: pointer;
		font: inherit;
		color: var(--text-h);
		text-align: left;
	}

	button:hover {
		background: var(--glass-bg-nested-active);
	}

	img {
		width: 22px;
		height: 22px;
		border-radius: 6px;
		object-fit: cover;
		flex-shrink: 0;
	}

	.name {
		flex: 1;
		font-size: 13px;
		font-weight: 600;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.rate {
		font-size: 12px;
		font-weight: 700;
		color: var(--accent);
		flex-shrink: 0;
	}
</style>
