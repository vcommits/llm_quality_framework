/**
 * ARENA MANAGER: "Gladiator Pit" Logic
 * Manages the list of contestants and the two-tier selection flow.
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

        const id = `fighter-${this.contestants.length}`;
        const slot = document.createElement('div');
        slot.className = 'fighter-slot';
        slot.id = id;

        // Simplified two-tier dropdown for now
        slot.innerHTML = `
            <select class="fighter-select" data-id="${id}">
                <!-- Options hydrated by main script -->
            </select>
            <button type="button" class="remove-fighter-btn" data-id="${id}">X</button>
        `;

        this.container.appendChild(slot);
        const select = slot.querySelector('select');
        
        // Populate with models
        window.modelRegistry.forEach(m => {
            select.appendChild(new Option(m.name, m.id));
        });

        if(modelId) select.value = modelId;

        const contestant = { id, selectElement: select };
        this.contestants.push(contestant);

        slot.querySelector('.remove-fighter-btn').addEventListener('click', () => this.removeContestant(id));
        
        if (this.contestants.length >= this.maxContestants) {
            this.addBtn.disabled = true;
        }
    }

    removeContestant(id) {
        const slot = document.getElementById(id);
        if (slot) this.container.removeChild(slot);

        this.contestants = this.contestants.filter(c => c.id !== id);
        this.addBtn.disabled = false;
    }

    getActiveModels() {
        return this.contestants.map(c => c.selectElement.value);
    }
}

class TransitionManager {
    constructor() {
        this.queue = [];
    }

    scheduleForProbe(modelId) {
        if (!this.queue.includes(modelId)) {
            this.queue.push(modelId);
            // In a real UI, you'd update a draggable list here
            console.log(`Queued for Interactive Probe: ${modelId}`);
        }
    }

    finishArena() {
        if (this.queue.length > 0) {
            const nextModel = this.queue.shift();
            console.log(`Transitioning to Interactive Probe with ${nextModel}`);
            // Here you would save session and switch tabs
            // For now, we just log it.
            alert(`Pivoting to Interactive Probe with ${nextModel}`);
        } else {
            alert("Arena session finished. No models queued for probe.");
        }
    }
}
