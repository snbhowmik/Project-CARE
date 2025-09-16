<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    // Group ID from route params
    const groupId = $page.params.id;

    // State variables
    let group: {
        name?: string;
        member?: Array<{ entity: { reference: string } }>;
    } | null = null;
    let allPatients: Array<any> = [];
    let selectedPatientId = '';
    let message = '';
    let messageType = '';

    async function fetchPageData() {
        const token = localStorage.getItem('authToken');
        if (!token) { goto('/login'); return; }

        // Fetch the specific group by its ID
        const groupRes = await fetch(`http://localhost:8080/fhir/Group/${groupId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (groupRes.ok) {
            group = await groupRes.json();
        }
        
        // Fetch all patients to populate the dropdown
        const patientsRes = await fetch('http://127.0.0.1:5000/patients/search?name=', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (patientsRes.ok) {
        if (patientsRes.ok) {
            const bundle = await patientsRes.json();
            allPatients = bundle.entry ? bundle.entry.map((e: { resource: any }) => e.resource) : [];
        }
    }}
    async function handleAddMember() {
        if (!selectedPatientId) return;
        message = '';
        const token = localStorage.getItem('authToken');
        if (!token) { goto('/login'); return; }

        const response = await fetch(`http://127.0.0.1:5000/group/${groupId}/members`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ patient_id: selectedPatientId })
        });
        
        if (response.ok) {
            messageType = 'success';
            message = "Member added successfully!";
            fetchPageData(); // Refresh the group details to show the new member
        } else {
            messageType = 'error';
            message = "Failed to add member.";
        }
    }

    onMount(fetchPageData);
</script>

<main>
    <a href="/groups" class="back-link">&larr; All Groups</a>
    {#if group}
        <h1>Group: <span class="group-name-header">{group.name}</span></h1>
        <div class="container">
            <div class="member-list card">
                <h2>Current Members ({group.member?.length || 0})</h2>
                {#if group.member && group.member.length > 0}
                    <ul>
                        {#each group.member as member}
                            <li>{member.entity.reference}</li>
                        {/each}
                    </ul>
                {:else}
                    <p>No patients have been added to this group yet.</p>
                {/if}
            </div>
            <div class="add-member card">
                <h2>Add Patient to Group</h2>
                <form on:submit|preventDefault={handleAddMember}>
                    <div class="form-group">
                        <label for="patient-select">Select Patient</label>
                        {#if allPatients.length > 0}
                            <select id="patient-select" bind:value={selectedPatientId} required>
                                <option value="" disabled>-- Choose a patient to add --</option>
                                {#each allPatients as patient (patient.id)}
                                    <option value={patient.id}>{patient.name[0].text} (ID: {patient.id.substring(0,8)}...)</option>
                                {/each}
                            </select>
                        {:else}
                            <p class="no-patients-msg">No patients found. <a href="/add-patient">Register a new patient</a> first.</p>
                        {/if}
                    </div>
                    <button type="submit" disabled={!selectedPatientId || allPatients.length === 0}>Add Member</button>
                    {#if message}
                        <p class="message {messageType}">{message}</p>
                    {/if}
                </form>
            </div>
        </div>
    {:else}
        <p>Loading group details...</p>
    {/if}
</main>

<style>
    /* Add styles for your detail page, which can be similar to the main groups page */
    main { max-width: 1200px; margin: 2rem auto; padding: 2rem; }
    h1 { text-align: center; margin-bottom: 3rem; color: #f9fafb; }
    .group-name-header { color: #3b82f6; }
    .back-link { display: block; margin-bottom: 2rem; color: #3b82f6; text-decoration: none; font-weight: bold; }
    .container { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: flex-start; }
    .card { background-color: #1f2937; padding: 2rem; border-radius: 12px; border: 1px solid #374151; }
    h2 { margin-top: 0; color: #e5e7eb; border-bottom: 1px solid #374151; padding-bottom: 1rem; margin-bottom: 1rem;}
    ul { list-style: none; padding: 0; }
    li { background-color: #374151; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; font-family: monospace; color: #9ca3af; }
    .form-group { margin-bottom: 1.5rem; }
    label { display: block; margin-bottom: 0.5rem; }
    select { width: 100%; padding: 0.75rem; background-color: #374151; border: 1px solid #4b5563; border-radius: 8px; color: #f9fafb; font-size: 1rem; box-sizing: border-box; }
    button { width: 100%; padding: 0.75rem; background-color: #3b82f6; border: none; border-radius: 8px; color: white; font-weight: 600; cursor: pointer; }
    button:disabled { background-color: #4b5563; cursor: not-allowed; }
    .message { margin-top: 1rem; padding: 0.75rem; border-radius: 6px; }
    .message.success { color: #22c55e; background-color: rgba(34, 197, 94, 0.1); }
    .message.error { color: #ef4444; background-color: rgba(239, 68, 68, 0.1); }
    .no-patients-msg { color: #9ca3af; }
    .no-patients-msg a { color: #3b82f6; }
</style>