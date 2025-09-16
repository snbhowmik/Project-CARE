<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>C.A.R.E. - Clinical Action and Response Engine</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin='anonymous'>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap" rel="stylesheet">
    
    <style>
        /* CSS RESET */
        :root {
            --color-primary: #2980b9;
            --color-secondary: #2c3e50;
            --color-text: #34495e;
            --color-text-light: #555;
            --color-bg: #f5f7fa;
            --color-white: #ffffff;
            --shadow: 0 10px 30px rgba(0, 0, 0, 0.07);
            --border-radius: 12px;
        }

        *, *::before, *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Inter', Arial, sans-serif;
            background-color: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
        }
        
        /* LAYOUT & MAIN STYLES */
        main {
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 1.5rem 4rem;
        }

        /* HERO SECTION */
        .hero {
            text-align: center;
            padding: 6rem 1rem;
            margin: 2rem 0;
            border-radius: var(--border-radius);
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: var(--color-white);
        }

        h1 {
            font-weight: 900;
            font-size: 3.5rem;
            line-height: 1.1;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        h1 small {
            font-weight: 500;
            color: #ecf0f1;
            font-size: 1.5rem;
            display: block;
            margin-top: 0.5rem;
        }

        .lead {
            font-size: 1.3rem;
            line-height: 1.7;
            max-width: 750px;
            margin: 1rem auto 0;
            opacity: 0.9;
        }
        
        /* --- NEW BUTTON STYLE --- */
        .cta-button {
            display: inline-block;
            margin-top: 2.5rem;
            padding: 1rem 2.5rem;
            background-color: var(--color-white);
            color: var(--color-primary);
            font-weight: 700;
            font-size: 1rem;
            text-decoration: none;
            border-radius: 50px; /* Pill shape */
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .cta-button:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        /* --- END NEW BUTTON STYLE --- */

        /* GENERAL SECTION STYLING */
        section {
            margin-top: 3.5rem;
            background: var(--color-white);
            border-radius: var(--border-radius);
            padding: 3rem;
            box-shadow: var(--shadow);
        }

        h2 {
            font-weight: 700;
            font-size: 2rem;
            color: var(--color-secondary);
            margin-bottom: 2rem;
            text-align: center;
        }

        h3 {
            font-size: 1.4rem;
            color: var(--color-primary);
            margin-bottom: 0.5rem;
            margin-top: 1.5rem;
        }
        h3:first-of-type {
            margin-top: 0;
        }

        p {
            margin-bottom: 1rem;
            max-width: 800px;
        }

        /* STATUS KEY SECTION */
        .status-key {
            display: flex;
            gap: 2rem;
            margin-top: 2.5rem;
            flex-wrap: wrap;
            justify-content: center;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            min-width: 200px;
        }

        .status-dot {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            flex-shrink: 0;
            position: relative;
        }
        .status-dot::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 50%;
            box-shadow: 0 0 8px 3px currentColor;
            opacity: 0.7;
        }

        @keyframes flash {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.95); }
        }
        
        /* CORE CONCEPTS CARDS */
        .concepts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        .concept-card {
            background-color: #fdfdfd;
            border: 1px solid #eef;
            border-radius: var(--border-radius);
            padding: 2rem;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .concept-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 35px rgba(41, 128, 185, 0.15);
        }
        .concept-card .icon {
            width: 60px;
            height: 60px;
            margin: 0 auto 1.5rem;
            background-color: rgba(41, 128, 185, 0.1);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--color-primary);
        }
        .concept-card h3 {
            margin-top: 0;
            font-size: 1.3rem;
            color: var(--color-secondary);
        }
        .concept-card p {
            font-size: 0.95rem;
            color: var(--color-text-light);
            margin-bottom: 0;
        }

        /* TEAM SECTION CARDS */
        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 2rem;
            text-align: center;
        }
        .team-member {
            transition: transform 0.3s ease;
        }
        .team-member:hover {
            transform: translateY(-5px);
        }
        .team-member img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 1rem;
            border: 4px solid var(--color-white);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .team-member .name {
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--color-secondary);
        }
        .team-member .role {
            font-size: 0.9rem;
            color: var(--color-primary);
        }
        
        /* FOOTER */
        .footer {
            text-align: center;
            margin-top: 4rem;
            font-size: 0.9rem;
            color: #888;
        }

        /* RESPONSIVE DESIGN */
        @media (max-width: 768px) {
            h1 {
                font-size: 2.8rem;
            }
            .lead {
                font-size: 1.1rem;
            }
            .hero {
                padding: 4rem 1rem;
            }
            section {
                padding: 2rem 1.5rem;
            }
        }
    </style>
</head>
<body>

    <main>
        <header class="hero">
            <h1>C.A.R.E.
                <small>Clinical Action and Response Engine</small>
            </h1>
            <p class="lead">
                Empowering every emergency room with clarity, focus, and life-saving expert guidance — no matter how small the hospital.
            </p>
            
            <a href="/dashboard" class="cta-button">Launch Dashboard</a>
            </header>

        <section aria-labelledby="vision-heading">
            <h2 id="vision-heading">The Vision: What We're Building and Why</h2>
            
            <h3>🚨 The Problem:</h3>
            <p>
                In India, small and rural hospitals are the front line of healthcare. When a major accident or health crisis occurs, they are often overwhelmed. Doctors face chaotic emergency rooms, trying to make life-or-death decisions based on fragmented information, losing precious time figuring out who needs help most urgently.
            </p>

            <h3>💡 The Solution: C.A.R.E.</h3>
            <p>
                We are building a smart, central "mission control" screen for emergency rooms. It automatically shows doctors which patient needs help right now (flashing red!), who is next (orange), and who is stable (green). Beyond that, it acts like a super-smart assistant, suggesting life-saving treatments based on thousands of similar cases from hospitals nationwide.
            </p>

            <div class="status-key" aria-label="Patient Status Indicators">
                <div class="status-item">
                    <span class="status-dot" style="color: #d32f2f; background-color: #d32f2f; animation: flash 1.5s infinite;"></span>
                    <div><strong>Critical (Red)</strong><br><small>Needs help right NOW</small></div>
                </div>
                <div class="status-item">
                    <span class="status-dot" style="color: #f57c00; background-color: #f57c00;"></span>
                    <div><strong>Urgent (Orange)</strong><br><small>Next in line for action</small></div>
                </div>
                <div class="status-item">
                    <span class="status-dot" style="color: #388e3c; background-color: #388e3c;"></span>
                    <div><strong>Stable (Green)</strong><br><small>Under control</small></div>
                </div>
            </div>
        </section>

        <section aria-labelledby="concepts-heading">
            <h2 id="concepts-heading">Core Concepts Explained</h2>
            <div class="concepts-grid">
                <article class="concept-card">
                    <div class="icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
                    </div>
                    <h3>🧠 Edge Computing</h3>
                    <p>The "Local Brain"—our C.A.R.E. Hub—sits in the ER, analyzing data instantly for rapid, reliable alerts, even with unstable internet.</p>
                </article>
                <article class="concept-card">
                    <div class="icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path></svg>
                    </div>
                    <h3>☁️ The Cloud</h3>
                    <p>The "National Expert Library" where our AI learns from millions of cases to provide doctors with evidence-based treatment suggestions.</p>
                </article>
                <article class="concept-card">
                    <div class="icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.72"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.72-1.72"></path></svg>
                    </div>
                    <h3>🌐 FHIR Standard</h3>
                    <p>The "Universal Translator" that lets different hospital systems speak the same language, enabling secure data sharing across the network.</p>
                </article>
            </div>
        </section>

        <section aria-labelledby="team-heading">
            <h2 id="team-heading">Meet the Team</h2>
            <p style="text-align: center; margin: -1.5rem auto 2.5rem;">
                We are a passionate group of engineers, doctors, and healthcare professionals dedicated to transforming emergency care in India.
            </p>
            <div class="team-grid">
                <div class="team-member">
                    <img src="https://placehold.co/120x120/3498db/ffffff?text=SNB" alt="Portrait of Subir Nath Bhowmik">
                    <div class="name">Subir Nath Bhowmik</div>
                    <div class="role">Software Engineer & Co-Founder</div>
                </div>
                <div class="team-member">
                    <img src="https://placehold.co/120x120/3498db/ffffff?text=NV" alt="Portrait of Nandakishore V">
                    <div class="name">Nandakishore V</div>
                    <div class="role">Data Scientist & Medical Researcher</div>
                </div>
                <div class="team-member">
                    <img src="https://placehold.co/120x120/3498db/ffffff?text=SKS" alt="Portrait of Shivani Kumari Singh">
                    <div class="name">Shivani Kumari Singh</div>
                    <div class="role">Full-Stack Developer</div>
                </div>
                <div class="team-member">
                    <img src="https://placehold.co/120x120/3498db/ffffff?text=DS" alt="Portrait of Devaganesh S">
                    <div class="name">Devaganesh S</div>
                    <div class="role">UX/UI Designer</div>
                </div>
            </div>
        </section>

    </main>

    <footer class="footer">
        <p>&copy; 2025 C.A.R.E. Initiative. All rights reserved.</p>
    </footer>

</body>
</html>