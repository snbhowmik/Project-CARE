<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    /** @type {any[]} */
    let groups: any[] = [];
    let newGroupName = '';
    let newGroupType = 'snakebite'; // Defaulting to snakebite for the demo
    let isLoading = true;
    let errorMessage = '';

    async function fetchGroups() {
        isLoading = true;
        const token = localStorage.getItem('authToken');
        if (!token) { goto('/login'); return; }

        try {
            const response = await fetch('http://127.0.0.1:5000/groups', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const bundle = await response.json();
                groups = bundle.entry ? bundle.entry.map((e: any) => e.resource) : [];
            } else {
                errorMessage = "Failed to load groups.";
            }
        } catch (error) {
            errorMessage = "Could not connect to the server.";
        }
        isLoading = false;
    }

    async function handleCreateGroup() {
        if (!newGroupName) return;
        const token = localStorage.getItem('authToken');
        if (!token) { goto('/login'); return; }

        await fetch('http://127.0.0.1:5000/group', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ name: newGroupName, type: newGroupType })
        });
        
        newGroupName = '';
        fetchGroups(); // Refresh the list after creating
    }
    
    /**
     * @param {string} groupId
     * @param {boolean} newStatus
     */
    async function updateGroupStatus(groupId: string, newStatus: boolean) {
        const token = localStorage.getItem('authToken');
        if (!token) { goto('/login'); return; }

        await fetch(`http://127.0.0.1:5000/group/${groupId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ active: newStatus })
        });
        
        fetchGroups(); // Refresh the list to show the change
    }

    onMount(fetchGroups);
</script>

<main>
    <a href="/dashboard" class="back-link">&larr; Back to Dashboard</a>
    <h1>Manage Patient Groups</h1>
    
    <div class="container">
        <div class="group-list card">
            <h2>Existing Groups</h2>
            {#if isLoading}
                <p>Loading groups...</p>
            {:else if groups.length === 0}
                <p>No groups found. Create one to get started.</p>
            {:else}
                <ul>
                    {#each groups as group (group.id)}
                        <li class:inactive={!group.active}>
                            <a href="/groups/{group.id}" class="group-info">
                                <span class="status-dot" class:active={group.active}></span>
                                <div class="name-details">
                                    <span class="group-name">{group.name}</span>
                                    <span class="member-count">{group.member?.length || 0} Members</span>
                                </div>
                            </a>
                            <button 
                                class="status-toggle" 
                                on:click={() => updateGroupStatus(group.id, !group.active)}>
                                {group.active ? 'Deactivate' : 'Activate'}
                            </button>
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>

        <div class="create-group card">
            <h2>Create New Group</h2>
            <form on:submit|preventDefault={handleCreateGroup}>
                <div class="form-group">
                    <label for="group-name">Group Name</label>
                    <input id="group-name" type="text" bind:value={newGroupName} placeholder="e.g., Highway 8 Accident" required />
                </div>
                <div class="form-group">
                    <label for="group-type">Analysis Type</label>
                    <select id="group-type" bind:value={newGroupType}>
                        <option value="snakebite">Snakebite Incident</option>
                        <option value="general">General</option>
                    </select>
                </div>
                <button type="submit">Create Group</button>
            </form>
        </div>
    </div>
</main>

<style>
    /* Styles for a clean, two-column layout that matches the dark theme */
    main { max-width: 1200px; margin: 2rem auto; padding: 2rem; }
    h1 { text-align: center; margin-bottom: 3rem; color: #f9fafb; }
    .back-link { display: block; margin-bottom: 2rem; color: #3b82f6; text-decoration: none; font-weight: bold; }
    
    .container {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 2rem;
        align-items: flex-start;
    }

    .card {
        background-color: #1f2937;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #374151;
    }

    h2 { margin-top: 0; color: #e5e7eb; border-bottom: 1px solid #374151; padding-bottom: 1rem; margin-bottom: 1rem; }
    
    ul { list-style: none; padding: 0; }
    li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #374151;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        transition: all 0.2s;
    }
    li.inactive { opacity: 0.6; }
    .group-info { display: flex; align-items: center; gap: 1rem; padding: 1rem; color: #d1d5db; text-decoration: none; flex-grow: 1; }
    .status-dot { height: 12px; width: 12px; background-color: #6b7280; border-radius: 50%; flex-shrink: 0; }
    .status-dot.active { background-color: #22c55e; }
    .name-details { display: flex; flex-direction: column; }
    .group-name { font-weight: 600; }
    .member-count { font-size: 0.8rem; color: #9ca3af; margin-top: 0.2rem; }

    .status-toggle {
        margin-right: 1rem;
        padding: 0.4rem 0.8rem;
        border: 1px solid #6b7280;
        background-color: transparent;
        color: #d1d5db;
        border-radius: 6px;
        cursor: pointer;
        white-space: nowrap;
    }
    li.inactive .status-toggle { border-color: #22c55e; color: #22c55e; }

    /* Form Styles */
    .form-group { margin-bottom: 1.5rem; }
    label { display: block; margin-bottom: 0.5rem; }
    input, select { width: 100%; padding: 0.75rem; background-color: #374151; border: 1px solid #4b5563; border-radius: 8px; color: #f9fafb; font-size: 1rem; box-sizing: border-box; }
    button { width: 100%; padding: 0.75rem; background-color: #3b82f6; border: none; border-radius: 8px; color: white; font-weight: 600; cursor: pointer; }
</style>