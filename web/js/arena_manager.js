/**
 * ARENA MANAGER: "Gladiator Pit" Logic
 * Manages the dynamic list of contestants for multi-model battles.
 */
class ArenaManager {
    constructor(maxContestants = 5) {
        this.contestants = [];
        this.maxContestants = maxContestants;
        this.container = document.getElementById('fighter-slots-container');
        this.addBtn = document.getElementById('add-fighter-btn');
        
        this.addBtn.addEventListener('click', () => this.addContestantSlot());
    }

    addContestantSlot(modelId = null) {
        if (this.contestants.length >= this.maxContestants) {
            this.addBtn.disabled = true;
            return;
        }

        const id = `fighter-${Date.now()}`;
        const slot = document.createElement('div');
        slot.className = 'fighter-slot';
        slot.id = id;
        
        // Two-tier dropdown logic will be handled by the main script's boot sequence
        slot.innerHTML = `
            <div class="fighter-card">
                <select class="fighter-provider-select" data-id="${id}"></select>
                <select class="fighter-model-select" data-id="${id}"></select>
                <button type="button" class="remove-fighter-btn" data-id="${id}">X</button>
            </div>
        `;

        this.container.appendChild(slot);
        const contestant = { 
            id, 
            element: slot,
            providerSelect: slot.querySelector('.fighter-provider-select'),
            modelSelect: slot.querySelector('.fighter-model-select')
        };
        this.contestants.push(contestant);

        slot.querySelector('.remove-fighter-btn').addEventListener('click', () => this.removeContestant(id));
        
        if (this.contestants.length >= this.maxContestants) {
            this.addBtn.disabled = true;
        }
        return contestant;
    }

    removeContestant(id) {
        const slot = document.getElementById(id);
        if (slot) this.container.removeChild(slot);

        this.contestants = this.contestants.filter(c => c.id !== id);
        this.addBtn.disabled = false;
    }

    getActiveModels() {
        return this.contestants.map(c => c.modelSelect.value);
    }
}
