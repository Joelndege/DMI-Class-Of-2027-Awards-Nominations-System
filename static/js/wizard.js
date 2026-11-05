document.addEventListener('DOMContentLoaded', () => {
    const steps = Array.from(document.querySelectorAll('.wizard-step'));
    if (!steps.length) return;

    const totalSteps = steps.length;
    const currentStepDisplay = document.getElementById('current-step-display');
    const progressBar = document.getElementById('progress-bar');
    const saveIndicator = document.getElementById('save-indicator');
    const stepPills = Array.from(document.querySelectorAll('.step-pill'));

    // Helper: get CSRF token
    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content');
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    // Determine starting step from URL query param ?step=
    const urlParams = new URLSearchParams(window.location.search);
    let currentStep = parseInt(urlParams.get('step'), 10) || 1;
    if (currentStep < 1 || currentStep > totalSteps) currentStep = 1;

    function showSaveIndicator() {
        if (!saveIndicator) return;
        saveIndicator.style.opacity = '1';
        setTimeout(() => {
            saveIndicator.style.opacity = '0';
        }, 1800);
    }

    function updateStep(newStep) {
        if (newStep < 1) newStep = 1;
        if (newStep > totalSteps) {
            window.location.href = '/nominate/review/';
            return;
        }

        currentStep = newStep;

        // Show active step card, hide others
        steps.forEach((stepEl) => {
            const stepNum = parseInt(stepEl.getAttribute('data-step'), 10);
            if (stepNum === currentStep) {
                stepEl.classList.remove('hidden');
                stepEl.classList.add('active');
            } else {
                stepEl.classList.remove('active');
                stepEl.classList.add('hidden');
            }
        });

        // Update step counter & progress bar
        if (currentStepDisplay) currentStepDisplay.textContent = currentStep;
        if (progressBar) {
            const percentage = Math.round((currentStep / totalSteps) * 100);
            progressBar.style.width = `${percentage}%`;
        }

        // Update pills
        stepPills.forEach((pill) => {
            const pillStep = parseInt(pill.getAttribute('data-step'), 10);
            if (pillStep === currentStep) {
                pill.classList.add('ring-2', 'ring-amber-400');
            } else {
                pill.classList.remove('ring-2', 'ring-amber-400');
            }
        });

        // Update Previous button state on step 1
        const activeCard = steps.find(s => parseInt(s.getAttribute('data-step'), 10) === currentStep);
        if (activeCard) {
            const prevBtn = activeCard.querySelector('.btn-prev');
            if (prevBtn) {
                prevBtn.disabled = currentStep === 1;
            }
        }

        // Scroll smoothly to top of wizard
        const container = document.getElementById('wizard-container');
        if (container) {
            const rect = container.getBoundingClientRect();
            if (rect.top < 0) {
                window.scrollTo({ top: window.scrollY + rect.top - 100, behavior: 'smooth' });
            }
        }
    }

    // Save step draft via AJAX
    async function saveStep(stepEl, skipped = false) {
        const categoryId = stepEl.getAttribute('data-category-id');
        const acceptsOnline = stepEl.getAttribute('data-accepts-online') === 'true';

        let payload = {
            category_id: categoryId,
            skipped: skipped || !acceptsOnline,
            nom_a_first: '',
            nom_a_last: '',
            nom_a_programme: '',
            nom_b_first: '',
            nom_b_last: '',
            nom_b_programme: '',
        };

        if (acceptsOnline && !skipped) {
            const aFirst = stepEl.querySelector(`[name="nom_a_first_${categoryId}"]`);
            const aLast = stepEl.querySelector(`[name="nom_a_last_${categoryId}"]`);
            const aProg = stepEl.querySelector(`[name="nom_a_programme_${categoryId}"]`);

            const bFirst = stepEl.querySelector(`[name="nom_b_first_${categoryId}"]`);
            const bLast = stepEl.querySelector(`[name="nom_b_last_${categoryId}"]`);
            const bProg = stepEl.querySelector(`[name="nom_b_programme_${categoryId}"]`);

            payload.nom_a_first = aFirst ? aFirst.value.trim() : '';
            payload.nom_a_last = aLast ? aLast.value.trim() : '';
            payload.nom_a_programme = aProg ? aProg.value.trim() : '';

            payload.nom_b_first = bFirst ? bFirst.value.trim() : '';
            payload.nom_b_last = bLast ? bLast.value.trim() : '';
            payload.nom_b_programme = bProg ? bProg.value.trim() : '';
        }

        try {
            const response = await fetch('/nominate/save-draft/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                showSaveIndicator();
                // Update corresponding step pill styling
                const stepNum = parseInt(stepEl.getAttribute('data-step'), 10);
                const pill = stepPills.find(p => parseInt(p.getAttribute('data-step'), 10) === stepNum);
                if (pill) {
                    if (skipped) {
                        pill.className = 'step-pill flex-shrink-0 w-8 h-8 rounded-lg border text-xs font-heading font-bold flex items-center justify-center transition-all border-neutral-700 bg-neutral-800/80 text-neutral-500';
                    } else if (payload.nom_a_first || payload.nom_a_last) {
                        pill.className = 'step-pill flex-shrink-0 w-8 h-8 rounded-lg border text-xs font-heading font-bold flex items-center justify-center transition-all border-amber-500/60 bg-amber-500/20 text-amber-300';
                    }
                }
                return true;
            }
        } catch (err) {
            console.error('Autosave error:', err);
        }
        return false;
    }

    // Attach step event listeners
    steps.forEach((stepEl) => {
        const prevBtn = stepEl.querySelector('.btn-prev');
        const nextBtn = stepEl.querySelector('.btn-next');
        const skipBtn = stepEl.querySelector('.btn-skip');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                saveStep(stepEl, false);
                updateStep(currentStep - 1);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', async () => {
                await saveStep(stepEl, false);
                updateStep(currentStep + 1);
            });
        }

        if (skipBtn) {
            skipBtn.addEventListener('click', async () => {
                await saveStep(stepEl, true);
                updateStep(currentStep + 1);
            });
        }

        // Autosave debounce on input change
        let debounceTimer;
        stepEl.querySelectorAll('.field-input').forEach((input) => {
            input.addEventListener('input', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    saveStep(stepEl, false);
                }, 800);
            });
        });
    });

    // Pill click navigation
    stepPills.forEach((pill) => {
        pill.addEventListener('click', async () => {
            const targetStep = parseInt(pill.getAttribute('data-step'), 10);
            const activeStepEl = steps.find(s => parseInt(s.getAttribute('data-step'), 10) === currentStep);
            if (activeStepEl) await saveStep(activeStepEl, false);
            updateStep(targetStep);
        });
    });

    // Initialize display
    updateStep(currentStep);
});

