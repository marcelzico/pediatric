document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('observation-main-form');
    if (!form) return;

    const obsId = form.dataset.obsId;
    const saveUrl = form.action; // Contient déjà ?ajax=1
    const statusBadge = document.getElementById('save-status');
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

    let saveTimeout;

    function updateStatus(text, type) {
        if (statusBadge) {
            statusBadge.textContent = text;
            statusBadge.className = `badge bg-${type} fs-6`;
        }
    }

    async function saveData() {
        // 1. Sauvegarde locale immédiate (File de sécurité)
        const formData = new FormData(form);
        const localData = {};
        formData.forEach((value, key) => {
            if (localData[key]) {
                if (!Array.isArray(localData[key])) localData[key] = [localData[key]];
                localData[key].push(value);
            } else {
                localData[key] = value;
            }
        });
        localStorage.setItem(`obs_draft_${obsId}`, JSON.stringify(localData));

        // 2. Vérification de la connexion
        if (!navigator.onLine) {
            updateStatus('⚠️ Hors ligne (Sauvegardé sur le PC)', 'warning');
            return;
        }

        updateStatus('⏳ Sauvegarde en cours...', 'secondary');

        // 3. Envoi au serveur
        try {
            const response = await fetch(saveUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });

            if (response.ok) {
                updateStatus('✅ Sauvegardé', 'success');
                // Optionnel : nettoyer le cache local si la synchro a réussi
                // localStorage.removeItem(`obs_draft_${obsId}`);
            } else {
                updateStatus('❌ Erreur serveur', 'danger');
            }
        } catch (error) {
            // Coupure réseau soudaine pendant l'envoi
            updateStatus('⚠️ Hors ligne (En attente de synchro)', 'warning');
        }
    }

    // Déclencheur sur modification (Debounce de 1.5s pour ne pas spammer le serveur)
    form.addEventListener('input', () => {
        clearTimeout(saveTimeout);
        updateStatus('✍️ Modifications non sauvegardées', 'info');
        saveTimeout = setTimeout(saveData, 1500);
    });

    // Déclencheur sur changement de select/checkbox (plus rapide)
    form.addEventListener('change', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(saveData, 500);
    });

    // 🌟 SYNCHRONISATION AUTOMATIQUE AU RETOUR DE LA CONNEXION 🌟
    window.addEventListener('online', () => {
        const draft = localStorage.getItem(`obs_draft_${obsId}`);
        if (draft) {
            updateStatus('🔄 Connexion rétablie, synchronisation...', 'info');
            saveData();
        }
    });
});