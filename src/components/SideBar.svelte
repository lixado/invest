<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import { slide } from "svelte/transition";
    import { formatNumber } from "../utils/utils";

    import LucideSidebarOpen from "virtual:icons/lucide/sidebar-open";
    import PhTrash from 'virtual:icons/ph/trash';
    import AddIcon from "virtual:icons/lucide/plus";
    import AutocompleteSelector from "./AutocompleteSelector.svelte";
    import type { AutocompleteOption, Bank, FundResult } from "../utils/models";

    const dispatch = createEventDispatcher();

    export let startAmount: number = 10000;
    export let monthlyContribution: number = 1000;
    export let fundsData: FundResult[] = [];
    export let banksData: Bank[] = [];
    export let funds: FundResult[] = [];
    export let banks: Bank[] = [];

    let startAmountInput: string = formatNumber(startAmount.toString());
    let monthlyContributionInput: string = formatNumber(
        monthlyContribution.toString(),
    );

    var showAddFundInput = false;
    var showAddBankInput = false;

    function addFund(event: CustomEvent) {
        const option: AutocompleteOption = event.detail.option;
        showAddFundInput = true;

        funds.push(fundsData[option.index]);

        dispatch("change");
        closeSidebar();
    }

    function addBank(event: CustomEvent) {
        const option: AutocompleteOption = event.detail.option;
        showAddBankInput = true;

        banks.push(banksData[option.index]);

        dispatch("change");
        closeSidebar();
    }

    function resetZoom() {
        dispatch("resetZoom");
    }

    function change() {
        startAmount = Number(startAmountInput.replace(/,/g, ""));
        monthlyContribution = Number(
            monthlyContributionInput.replace(/,/g, ""),
        );
        dispatch("change");
    }

    function closeSidebar() {
        dispatch("close");
    }
</script>

<main class="sidebar" transition:slide={{ duration: 300, axis: "x" }}>
    <button class="close-button" on:click={closeSidebar}
        ><LucideSidebarOpen style="rotate: 180deg;" /></button
    >

    <div class="sidebar-content">
        <button on:click={e => {
            resetZoom();
            closeSidebar()
        }}>Reset Zoom</button>
        <br />

        <div>
            <label for="startAmount"><b>Start Amount:</b></label>
            <input
                style="width: 60%; text-align: right;"
                type="text"
                id="startAmount"
                bind:value={startAmountInput}
                placeholder="Enter starting amount"
                on:input={(e) => {
                    startAmountInput = formatNumber(e.currentTarget.value);
                    change();
                }}
            />
        </div>

        <div>
            <label for="monthlyContribution"><b>Monthly Contribution:</b></label>
            <input
                style="width: 60%; text-align: right;"
                type="text"
                id="monthlyContribution"
                bind:value={monthlyContributionInput}
                placeholder="Enter monthly contribution"
                on:input={(e) => {
                    monthlyContributionInput = formatNumber(
                        e.currentTarget.value,
                    );
                    change();
                }}
            />
        </div>

        <div
            style="display: flex; align-items: center; justify-content: center; gap: 0.5em;white-space: nowrap;"
        >
            {#if showAddFundInput}
                <div transition:slide={{ duration: 75, axis: "x" }}>
                    <AutocompleteSelector options={fundsData.map((fund, index) => ({
                        index: index,
                        name: fund.instrument_info.name,
                        icon_url: fund.instrument_info.instrument_icon_url,
                        interest_rate: fund.annual_growth_info.annual_growth_1y
                    }))} on:select={addFund} />
                </div>
            {:else}
                <button style="display: flex; align-items: center; gap: 0.5em;"  on:click={(e) => {
                    showAddFundInput = true;
                }}>
                    <AddIcon /> Add Fund
                </button>
            {/if}
        </div>

        <div
            style="display: flex; align-items: center; justify-content: center; gap: 0.5em;white-space: nowrap;"
        >
            {#if showAddBankInput}
                <div transition:slide={{ duration: 75, axis: "x" }}>
                    <AutocompleteSelector options={banksData.map((bank, index) => ({
                        index: index,
                        name: bank.leverandorVisningsnavn + ` (${bank.navn})`,
                        icon_url: bank.leverandorUrl.endsWith('/') ? bank.leverandorUrl + 'favicon.ico' : bank.leverandorUrl + '/favicon.ico',
                        interest_rate: Number(bank.rentesats1)
                    }))} on:select={addBank} />
                </div>
            {:else}
                <button style="display: flex; align-items: center; gap: 0.5em;"  on:click={(e) => {
                    showAddBankInput = true;
                }}>
                    <AddIcon /> Add Bank
                </button>
            {/if}
        </div>

        <div
            style="display: flex; align-items: center; justify-content: center; gap: 0.5em;white-space: nowrap;"
        >
            {#if funds.length > 0 || banks.length > 0}
                <button style="display: flex; align-items: center; gap: 0.5em;" on:click={e => {
                    funds = [];
                    banks = [];
                    dispatch("change");
                }}>
                <PhTrash /> Clear All
                </button>
            {/if}
        </div>


    </div>
</main>

<style>
    .close-button {
        position: absolute;
        top: 50%;
        right: -75px; /* Adjust this value to position the button outside the sidebar */
        transform: translateY(-50%);
        z-index: 1000;
    }
    .sidebar-content {
        display: flex;
        gap: 1em;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }

    .sidebar {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        width: 250px;
        padding: 1rem;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        border-right: 1px solid #ccc;
        z-index: 1000; /* Add this line to ensure the sidebar appears above other elements */
    }

    label {
        display: block;
        margin-bottom: 0.5rem;
    }

    input {
        width: 100%;
        padding: 0.5rem;
    }
</style>
