<script>
    import { goto } from '$app/navigation';

    // NEW: State variables are now structured
    let givenName = '';
    let familyName = '';
    let birthDate = '';
    let gender = 'unknown';
    let phone = '';
    
    let line = '';
    let city = '';
    let state = '';
    let postalCode = '';
    let country = 'INDIA'; // Defaulting to India as per previous code

    let active = true;

    let isLoading = false;
    let message = '';
    let messageType = '';

    async function handleSubmit() {
        isLoading = true;
        message = '';
        const token = localStorage.getItem('authToken');

        if (!token) {
            goto('/login');
            return;
        }

        // NEW: Construct the nested JSON payload to match the FHIR structure
        const payload = {
            name: {
                given: givenName,
                family: familyName
            },
            telecom: {
                system: 'phone',
                use: 'home',
                value: phone
            },
            address: {
                line: line,
                city: city,
                state: state,
                postalCode: postalCode,
                country: country
            },
            gender: gender,
            birthDate: birthDate,
            active: active
        };

        const response = await fetch('http://127.0.0.1:5000/patient', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            messageType = 'success';
            message = 'Patient created successfully! Redirecting to search...';
            setTimeout(() => {
                goto('/search');
            }, 2000);
        } else {
            const data = await response.json();
            messageType = 'error';
            message = data.message || 'Failed to create patient.';
        }
        isLoading = false;
    }
</script>

<main>
    <a href="/dashboard" class="back-link">&larr; Back to Dashboard</a>
    <h1>Register New Patient</h1>
    
    <form on:submit|preventDefault={handleSubmit}>
        <fieldset>
            <legend>Patient Name</legend>
            <div class="form-grid">
                <div class="form-group">
                    <label for="givenName">Given Name (First Name)</label>
                    <input id="givenName" type="text" bind:value={givenName} required />
                </div>
                <div class="form-group">
                    <label for="familyName">Family Name (Last Name)</label>
                    <input id="familyName" type="text" bind:value={familyName} required />
                </div>
            </div>
        </fieldset>

        <fieldset>
            <legend>Demographics</legend>
            <div class="form-grid">
                <div class="form-group">
                    <label for="birthDate">Date of Birth</label>
                    <input id="birthDate" type="date" bind:value={birthDate} required />
                </div>
                <div class="form-group">
                    <label for="gender">Gender</label>
                    <select id="gender" bind:value={gender}>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                        <option value="unknown">Unknown</option>
                    </select>
                </div>
            </div>
        </fieldset>
        
        <fieldset>
            <legend>Contact Information</legend>
            <div class="form-group">
                <label for="telecom">Phone Number</label>
                <input id="telecom" type="tel" bind:value={phone} />
            </div>
            <div class="form-group">
                <label for="line">Address Line</label>
                <input id="line" type="text" bind:value={line} />
            </div>
            <div class="form-grid">
                <div class="form-group">
                    <label for="city">City</label>
                    <input id="city" type="text" bind:value={city} />
                </div>
                <div class="form-group">
                    <label for="state">State</label>
                    <input id="state" type="text" bind:value={state} />
                </div>
                <div class="form-group">
                    <label for="postalCode">Postal Code</label>
                    <input id="postalCode" type="text" bind:value={postalCode} />
                </div>
            </div>
        </fieldset>

        <div class="form-group-checkbox">
            <input id="active" type="checkbox" bind:checked={active} />
            <label for="active">Mark patient record as active</label>
        </div>

        <button type="submit" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Save Patient'}
        </button>
    </form>

    {#if message}
        <div class="message {messageType}">{message}</div>
    {/if}
</main>

<style>
    main { max-width: 800px; margin: 2rem auto; padding: 2rem; background: #fff; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
    h1 { text-align: center; color: #2c3e50; }
    .back-link { display: block; margin-bottom: 2rem; color: #3498db; text-decoration: none; font-weight: bold; }
    
    fieldset { border: 1px solid #e0e0e0; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
    legend { font-weight: 600; font-size: 1.2rem; color: #34495e; padding: 0 0.5rem; }

    .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
    .form-group { margin-bottom: 1rem; }
    label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
    input, select { width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; box-sizing: border-box; }
    
    .form-group-checkbox { display: flex; align-items: center; gap: 0.5rem; margin: 1.5rem 0; }
    .form-group-checkbox input { width: auto; }
    
    button { width: 100%; padding: 1rem; border: none; border-radius: 4px; background-color: #3498db; color: white; font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: background-color 0.2s; }
    button:hover { background-color: #2980b9; }
    button:disabled { background-color: #bdc3c7; }
    
    .message { margin-top: 1rem; padding: 1rem; border-radius: 4px; text-align: center; }
    .message.success { background-color: #e8f5e9; color: #2e7d32; }
    .message.error { background-color: #ffebee; color: #c62828; }
</style>