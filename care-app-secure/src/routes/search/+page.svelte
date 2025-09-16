<script lang="ts">
    import { onMount } from 'svelte';

    let searchTerm: string = '';
    type Patient = {
        id: string;
        name: { text: string }[];
        active: boolean;
        // add other fields as needed
    };
    let results: Patient[] = [];
    let message: string = '';

    async function search() {
        if (searchTerm.length < 2) {
            results = [];
            return;
        }
        const token = localStorage.getItem('authToken');
        const response = await fetch(`http://127.0.0.1:5000/patients/search?name=${searchTerm}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const bundle = await response.json();
            results = bundle.entry ? bundle.entry.map((e: { resource: Patient }) => e.resource) : [];
        }
    }

    async function activatePatient(patientId: string) {
        const token = localStorage.getItem('authToken');
        await fetch(`http://127.0.0.1:5000/patient/${patientId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ active: true })
        });
        message = `Patient ${patientId} has been activated and sent to the dashboard.`;
        // Remove the patient from the current search results
        results = results.filter(p => p.id !== patientId);
    }
</script>

<main>
    <a href="/dashboard" class="back-link">&larr; Back to Dashboard</a>
    <h1>Search & Activate Patients</h1>
    <div class="search-bar">
        <input type="search" bind:value={searchTerm} on:input={search} placeholder="Search by patient name..." />
    </div>
    
    {#if message}<p class="success-message">{message}</p>{/if}

    <div class="results-list">
        {#each results as patient (patient.id)}
            <div class="result-item">
                <div class="info">
                    <strong>{patient.name[0].text}</strong> (ID: {patient.id})
                    <span class="status" class:active={patient.active}>
                        {patient.active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                {#if !patient.active}
                    <button on:click={() => activatePatient(patient.id)}>Activate</button>
                {/if}
            </div>
        {/each}
    </div>
</main>
<style>
    /* Add styles for your search page */
    .search-bar {
        margin-bottom: 20px;
    }
    .results-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .result-item {
        display: flex;
        justify-content: space-between; 
    }
    .info {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .status {
        padding: 5px 10px;
    }       
</style>