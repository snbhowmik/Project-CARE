<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    // JSDoc typedefs to define our data structures
    /**
     * @typedef {{ resource: { resourceType: 'Patient', id: string, name: { text: string }[], active: boolean } }} FHIRPatientEntry
     * @typedef {{ resource: { resourceType: 'Observation', subject: { reference: string }, code: { coding: { code: string }[] }, valueQuantity: { value: number } } }} FHIRObservationEntry
     * @typedef {FHIRPatientEntry | FHIRObservationEntry} FHIREntry
     */

    /** @type {any[]} */
    let patients = [];
    
    /** @type {Object<string, any>} */
    let observations = {};

    let lastUpdated = new Date();

    /** @type {Record<string, string>} */
    const LOINC_MAP = {
        '8867-4': 'heart_rate', '59408-5': 'spo2', '9279-1': 'respiratory_rate',
        '8310-5': 'temperature', '8480-6': 'bp_systolic', '8462-4': 'bp_diastolic',
        '2339-0': 'blood_sugar', '2951-2': 'sodium', '2823-3': 'potassium',
        '11558-4': 'ph', '2019-8': 'paco2', '2703-7': 'pao2', '9269-2': 'gcs'
    };

    async function fetchData() {
        const token = localStorage.getItem('authToken');
        if (!token) { goto('/login'); return; }

        try {
            // This URL now correctly fetches only ACTIVE patients for the dashboard
            const response = await fetch('http://127.0.0.1:5000/patients', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (response.status === 401) { goto('/login'); return; }

            if (response.ok) {
                const bundle = await response.json();
                
                patients = bundle.entry
                    ? bundle.entry.filter(/** @param {FHIREntry} e */ e => e.resource.resourceType === 'Patient').map(/** @param {FHIRPatientEntry} e */ e => e.resource)
                    : [];

                const obsEntries = bundle.entry
                    ? bundle.entry.filter(/** @param {FHIREntry} e */ e => e.resource.resourceType === 'Observation')
                    : [];
                
                /** @type {Object<string, any>} */
                const newObservations = {};
                obsEntries.forEach(/** @param {FHIRObservationEntry} o */ o => {
                    const patientId = o.resource.subject.reference.split('/')[1];
                    if (!newObservations[patientId]) {
                        newObservations[patientId] = {};
                    }
                    const loincCode = o.resource.code.coding[0].code;
                    const obsName = LOINC_MAP[loincCode];
                    if (obsName) {
                        newObservations[patientId][obsName] = o.resource.valueQuantity.value;
                    }
                });
                observations = newObservations;
                lastUpdated = new Date();
            }
        } catch (error) {
            console.error("Failed to fetch data:", error);
        }
    }
    
    // This is the single, correct version of the function
    /**
     * @param {string} patientId
     * @param {boolean} newStatus
     */
    async function updatePatientStatus(patientId, newStatus) {
        const token = localStorage.getItem('authToken');
        if (!token) { goto('/login'); return; }

        await fetch(`http://127.0.0.1:5000/patient/${patientId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ active: newStatus })
        });
        
        // Instantly remove the patient from the UI if they are deactivated
        if (newStatus === false) {
            patients = patients.filter(p => p.id !== patientId);
        } else {
            fetchData();
        }
    }

    /** @param {any} patient */
    function getStatus(patient) {
        const obs = observations[patient.id] || {};
        const hr = obs.heart_rate || 0;
        const spo2 = obs.spo2 || 100;
        if (spo2 < 92 || hr > 140) return "RED";
        if (hr > 120 || spo2 < 95) return "ORANGE";
        return "GREEN";
    }

    onMount(() => {
        fetchData();
        setInterval(fetchData, 5000);
    });
</script>

<main>
    <header>
        <div class="header-title">
            <img src="src/lib/assets/favicon.png" alt="C.A.R.E. Logo" />
            <h1>Mission Control</h1>
        </div>
        <div class="header-actions">
            <span class="last-updated">
                Last Updated: {lastUpdated.toLocaleTimeString()}
            </span>
            <a href="/search" class="nav-btn">Search</a>
            <a href="/groups" class="nav-btn">Manage Groups</a>
            <a href="/add-patient" class="add-patient-btn">＋ Register Patient</a>
        </div>
    </header>
  
  <div class="dashboard">
    {#if patients.length > 0}
        {#each patients as patient (patient.id)}
            {@const status = getStatus(patient)}
            {@const obs = observations[patient.id] || {}}

            <div class="card {status.toLowerCase()}" class:inactive={!patient.active}>
                <div class="card-header">
                    <div class="patient-info">
                        <h2>{patient.name[0].text}</h2>
                        <span class="patient-id">ID: {patient.id.substring(0, 8)}...</span>
                        <span class="status-tag">{status}</span>
                    </div>
                </div>

                <div class="data-grid">
                    <div class="data-section">
                        <p><span>❤️ HR</span> <strong>{obs.heart_rate || '--'}</strong> bpm</p>
                        <p><span>💨 SpO2</span> <strong>{obs.spo2 || '--'}</strong> %</p>
                        <p><span>BP</span> <strong>{obs.bp_systolic || '--'}/{obs.bp_diastolic || '--'}</strong> mmHg</p>
                        <p><span>RR</span> <strong>{obs.respiratory_rate || '--'}</strong> /min</p>
                    </div>
                    <div class="data-section">
                        <p><span>🌡️ Temp</span> <strong>{obs.temperature || '--'}</strong> °C</p>
                        <p><span>🩸 Sugar</span> <strong>{obs.blood_sugar || '--'}</strong> mg/dL</p>
                        <p><span>🧠 GCS</span> <strong>{obs.gcs || '--'}</strong> /15</p>
                    </div>
                    <div class="data-section labs">
                        <p><span>pH</span> <strong>{obs.ph || '--'}</strong></p>
                        <p><span>PaCO₂</span> <strong>{obs.paco2 || '--'}</strong></p>
                        <p><span>Na⁺</span> <strong>{obs.sodium || '--'}</strong></p>
                        <p><span>K⁺</span> <strong>{obs.potassium || '--'}</strong></p>
                    </div>
                </div>
                
                <div class="card-footer">
                    <button class="status-toggle-btn" on:click={() => updatePatientStatus(patient.id, !patient.active)}>
                        {patient.active ? 'Set Inactive' : 'Set Active'}
                    </button>
                </div>
            </div>
        {/each}
    {:else}
        <div class="loading-container">
            <div class="spinner"></div>
            <p class="loading-message">Connecting to C.A.R.E. Engine...</p>
        </div>
    {/if}
  </div>
</main>

<style>
    :global(body) {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #111827; /* Dark background */
        color: #d1d5db; /* Light gray text */
        margin: 0;
    }

    main {
        max-width: 1600px;
        margin: 0 auto;
        padding: 1.5rem 2rem;
    }

    header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #374151;
    }
    
    .header-title { display: flex; align-items: center; gap: 1rem; }
    .header-title img { height: 42px; }
    .header-title h1 { font-size: 1.75rem; color: #f9fafb; margin: 0; }

    .header-actions { display: flex; align-items: center; gap: 1.5rem; }
    .last-updated { font-size: 0.9rem; color: #9ca3af; }
    .add-patient-btn {
        background-color: #3b82f6;
        color: white;
        text-decoration: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .add-patient-btn:hover { background-color: #2563eb; }

    .dashboard {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 1.5rem;
    }

    .card {
        background-color: #1f2937; /* Darker card background */
        border-radius: 12px;
        border-top: 4px solid; /* Status border on top */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .card:hover { transform: translateY(-4px); }

    .card.inactive {
        filter: grayscale(80%);
        opacity: 0.6;
    }

    .card-header {
        padding: 1rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .patient-info h2 { font-size: 1.5rem; margin: 0 0 0.25rem 0; color: #f9fafb; }
    .patient-id { font-size: 0.8rem; color: #9ca3af; font-family: monospace; }
    
    .status-tag {
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        border-radius: 99px;
        font-size: 0.8rem;
        color: #111827;
        text-transform: uppercase;
    }

    .data-grid {
        padding: 0 1.5rem;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        flex-grow: 1;
    }
    .data-section { padding-top: 1rem; }
    .data-section.labs { border-top: 1px solid #374151; grid-column: 1 / -1; }
    
    .data-section p { display: flex; justify-content: space-between; margin: 0.6rem 0; font-size: 1rem; }
    .data-section p span { color: #9ca3af; }
    .data-section p strong { color: #f9fafb; font-weight: 600; }
    
    .card-footer {
        margin-top: auto;
        padding: 1rem 1.5rem;
        border-top: 1px solid #374151;
        text-align: right;
    }
    .status-toggle-btn {
        background: #4b5563;
        color: #e5e7eb;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    .status-toggle-btn:hover { background: #6b7280; }
    .inactive .status-toggle-btn { background: #16a34a; }
    .inactive .status-toggle-btn:hover { background: #15803d; }


    .nav-btn {
        background-color: #4b5563; /* A different color for navigation */
        color: white;
        text-decoration: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .nav-btn:hover {
        background-color: #6b7280;
    }

    
    /* Status Colors */
    .card.green { border-color: #22c55e; }
    .green .status-tag { background-color: #22c55e; }
    .card.orange { border-color: #f97316; }
    .orange .status-tag { background-color: #f97316; }
    .card.red { border-color: #ef4444; animation: pulseRed 2s infinite; }
    .red .status-tag { background-color: #ef4444; }

    /* Loading Spinner */
    .loading-container { grid-column: 1 / -1; display: flex; align-items: center; justify-content: center; padding: 4rem; color: #9ca3af; }
    .spinner { border: 4px solid #374151; width: 36px; height: 36px; border-radius: 50%; border-left-color: #3b82f6; animation: spin 1s ease infinite; margin-right: 1rem; }
    @keyframes spin { to { transform: rotate(360deg); } }
    
    /* Red Alert Animation */
    @keyframes pulseRed {
        0% { box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); }
        50% { box-shadow: 0 6px 30px rgba(239, 68, 68, 0.4); }
        100% { box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); }
    }
</style>