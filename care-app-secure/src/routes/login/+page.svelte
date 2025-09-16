<script>
    import { goto } from '$app/navigation';

    let username = '';
    let password = '';
    let error = '';
    let isLoading = false;

    async function handleLogin() {
        error = '';
        isLoading = true;
        try {
            const response = await fetch('http://127.0.0.1:5000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('authToken', data.token);
                goto('/dashboard');
            } else {
                error = data.message || "Login failed. Please try again.";
            }
        } catch (err) {
            error = "Could not connect to the server. Please check your connection.";
        }
        isLoading = false;
    }
</script>

<div class="login-container">
    <div class="login-box">
        <div class="login-header">
            <img src="src/lib/assets/favicon.png" alt="C.A.R.E. Logo" />
            <h1>Login</h1>
            <p>Clinical Action & Response Engine</p>
        </div>

        <form on:submit|preventDefault={handleLogin}>
            <div class="form-group">
                <label for="username">Username</label>
                <input id="username" type="text" bind:value={username} placeholder="e.g., doctor1" required />
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input id="password" type="password" bind:value={password} placeholder="••••••••••" required />
            </div>

            <button type="submit" disabled={isLoading}>
                {#if isLoading}
                    <div class="spinner"></div>
                    <span>Authenticating...</span>
                {:else}
                    Sign In
                {/if}
            </button>
        </form>

        {#if error}
            <div class="error-message">{error}</div>
        {/if}
    </div>
</div>

<style>
    :global(body) {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #111827; /* Dark background from dashboard */
        color: #d1d5db;
        margin: 0;
    }

    .login-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 2rem;
        box-sizing: border-box;
    }

    .login-box {
        width: 100%;
        max-width: 400px;
        padding: 2.5rem;
        background-color: #1f2937; /* Dark card background */
        border-radius: 16px;
        border: 1px solid #374151;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }

    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .login-header img {
        height: 60px;
        margin-bottom: 1rem;
    }

    .login-header h1 {
        color: #f9fafb;
        font-size: 2rem;
        margin: 0;
    }

    .login-header p {
        color: #9ca3af;
        margin: 0.25rem 0 0 0;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #d1d5db;
    }

    .form-group input {
        width: 100%;
        padding: 0.75rem 1rem;
        background-color: #374151;
        border: 1px solid #4b5563;
        border-radius: 8px;
        color: #f9fafb;
        font-size: 1rem;
        box-sizing: border-box;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    .form-group input:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
    }

    button {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.75rem;
        border: none;
        border-radius: 8px;
        background-color: #3b82f6;
        color: white;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    button:hover:not(:disabled) {
        background-color: #2563eb;
    }

    button:disabled {
        background-color: #4b5563;
        cursor: not-allowed;
    }

    .error-message {
        margin-top: 1.5rem;
        padding: 0.75rem;
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        color: #f87171;
        border-radius: 8px;
        text-align: center;
    }

    .spinner {
        border: 3px solid rgba(255, 255, 255, 0.3);
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border-left-color: #ffffff;
        animation: spin 1s ease infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>