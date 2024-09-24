<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import type { AutocompleteOption } from "../utils/models";

    export let options: AutocompleteOption[] = [];

    let inputValue: string = "";
    let filteredOptions: AutocompleteOption[] = [];
    const dispatch = createEventDispatcher();

    function handleInput(event: Event) {
        const target = event.target as HTMLInputElement;
        inputValue = target.value;

        filteredOptions = options.filter(option => {
            let contains = option.name?.toLowerCase().includes(inputValue.toLowerCase());
            if (contains) return true;
            return false;
        });

        // if filteredOptions len is 1 then choose that option
        if (filteredOptions.length === 1) {
            handleSelect(null, filteredOptions[0]);
        }
    }

    function handleSelect(event: Event | null, option: AutocompleteOption) {
        dispatch("select", { option: option });
    }

</script>


<main>
    <div>
        <div class="autocomplete">
            <input
                id="country-input"
                type="text"
                placeholder="Search ..."
                bind:value={inputValue}
                on:input={handleInput}
            />
        </div>
    
        <ul id="autocomplete-items-list">
            {#if inputValue.length == 0}
                <li class="recommended">Recommended options:</li>
                {#each options.filter(option => option.name?.toLowerCase().includes("dnb"))
                    .sort(() => Math.random() - 0.5) // random sort as to get different options if possible
                    .slice(0, 5) as option, i}
                    <button 
                    on:click={(event) => handleSelect(event, option)} 
                    on:keydown={(event) => event.key === 'Enter' && handleSelect(event, option)}
                    style="display: flex; align-items: center; justify-content: center; gap: 5px;">
                        {#if option.icon_url}
                            <img on:error={(e) => {null}} src={option.icon_url} alt={option.name} style="width: 20px; height: 20px;" />
                        {/if}
                        {option.name}
                    </button>
                {/each}
            {:else}
                {#each filteredOptions as option}
                    <button 
                    on:click={(event) => handleSelect(event, option)} 
                    on:keydown={(event) => event.key === 'Enter' && handleSelect(event, option)}
                    style="display: flex; align-items: center; justify-content: center; gap: 5px;">
                        {#if option.icon_url}
                            <img on:error={(e) => {option.icon_url = ""}} src={option.icon_url} alt={option.name} style="width: 20px; height: 20px;" />
                        {/if}
                        {option.name}
                    </button>
                {/each}
            {/if}
        </ul>
    </div>    
</main>

<style>
    div.autocomplete {
        /*the container must be positioned relative:*/
        position: relative;
        display: inline-block;
        width: 300px;
        margin-bottom: 1em;
    }

    #autocomplete-items-list {
        background-color: #ffffff;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        padding: 0;
        transition: box-shadow 0.3s ease-in-out;
        margin: 0;
        z-index: 9999;
        position: absolute;
        list-style: none; /* Remove default list styling */
        display: flex;
        flex-direction: column;
        left: 10px; /* Start at the left side of the panel with a margin of 10px */
        max-width: 95vw;
        max-height: 275px; /* Adjust this value based on your item height */
        overflow-y: auto;
    }

    #autocomplete-items-list button{
        border-radius: 0%;
        height: 50px; /* Set a fixed height for each item */
    }

    #autocomplete-items-list li {
        padding: 12px 16px;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    #autocomplete-items-list li:hover {
        background-color: #f1f1f1;
    }

    #autocomplete-items-list li:active {
        background-color: #e0e0e0;
    }

    #autocomplete-items-list:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Add this rule to prevent hover effect on "Recommended options:" */
    #autocomplete-items-list li.recommended:hover {
        background-color: initial;
    }

    @media (prefers-color-scheme: dark) {
        #autocomplete-items-list {
            background-color: #2c2c2c;
            color: rgba(255, 255, 255, 0.87);
        }

        #autocomplete-items-list li:hover {
            background-color: #3c3c3c;
        }

        #autocomplete-items-list li:active {
            background-color: #4c4c4c;
        }
    }
</style>
