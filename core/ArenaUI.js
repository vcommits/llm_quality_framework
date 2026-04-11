/**
 * GHIDORAH // CORE // ARENA_UI
 * Orchestrates the Discovery Flow, Sidebar States, and Arena Commitments.
 */
import { AssetManager } from './AssetManager.js';

export class ArenaUI {
    constructor(matchmaker) {
        this.matchmaker = matchmaker;
        this.assets = new AssetManager();
        this.fighters = [];
        this.init();
    }

    async init() {
        const ready = await this.matchmaker.hydrate();
        if (ready) {
            this.populate('provider');
            console.log("SENTRY: UI Orchestrator Online.");
        }
    }

    toggleSidebar() {
        document.getElementById('postman-sidebar').classList.toggle('closed');
    }

    handleSelect(level) {
        const select = document.getElementById(`pick-${level}`);
        this.matchmaker.selection[level] = select.value;

        // 1. AFFIRMATION: Trigger 200ms Green Pulse
        const step = document.getElementById(`step-${level}`);
        step.classList.add('confirmed');
        select.classList.add('selection-glow');

        // 2. BLOOM: Open Next Tier
        const flow = ['provider', 'type', 'tier', 'model'];
        const nextIdx = flow.indexOf(level) + 1;

        if (nextIdx < flow.length) {
            const nextLevel = flow[nextIdx];
            this.populate(nextLevel);
            document.getElementById(`step-${nextLevel}`).classList.add('active');
        } else {
            this.unlockSummon();
        }
    }

    populate(level) {
        const select = document.getElementById(`pick-${level}`);
        const options = this.matchmaker.getOptions(level);

        select.innerHTML = `<option value="" disabled selected>-- SELECT ${level.toUpperCase()} --</option>`;
        options.forEach(opt => {
            const val = typeof opt === 'string' ? opt : opt.id;
            const name = typeof opt === 'string' ? opt : opt.name;
            select.innerHTML += `<option value="${val}">${name}</option>`;
        });
    }

    unlockSummon() {
        const btn = document.getElementById('add-btn');
        btn.disabled = false;
        btn.classList.add('bg-accent-green', 'text-black', 'border-accent-green');
        btn.classList.remove('bg-white/5', 'text-white/20');
        btn.style.backgroundColor = '#00ff41';
    }

    commitFighter() {
        if (this.fighters.length >= 5) return;

        const modelId = this.matchmaker.selection.model;
        const model = this.matchmaker.models.find(m => m.id === modelId);

        this.fighters.push(model);

        // Lock Weightclass on first commit
        if (this.fighters.length === 1) {
            this.matchmaker.activeWeightclass = model.weightclass;
        }

        this.renderToSlot(model, this.fighters.length - 1);
        this.toggleSidebar();
        this.resetMatchmaker();
    }

    renderToSlot(model, index) {
        const slot = document.getElementById(`slot-${index}`);
        const hue = `hsl(${Math.random() * 360}, 70%, 50%)`;
        slot.classList.add('active');
        slot.style.setProperty('--fighter-hue', hue);
        slot.style.borderTop = `5px solid ${hue}`;

        slot.innerHTML = `
            <div class="flex flex-col h-full w-full p-4">
                <div class="flex justify-between items-start mb-2">
                    <div class="flex flex-col">
                        <span class="text-[9px] text-white/30 uppercase font-mono">${model.provider}</span>
                        <span class="text-xs font-bold text-white uppercase tracking-tight">${model.name}</span>
                    </div>
                </div>
                <div class="flex-grow bg-black/40 border border-white/5 p-3 text-[10px] text-cyan-300/40 italic overflow-y-auto font-mono" id="response-${index}">
                    AWAITING_DISPATCH...
                </div>
                <div class="mt-4 flex justify-between text-[8px] text-white/20 uppercase font-bold tracking-widest font-mono">
                    <span>${model.weightclass}</span>
                    <span>${model.tier}</span>
                </div>
            </div>
        `;
    }

    dispatchFight() {
        const prompt = document.getElementById('cmd-box').value;
        if (!prompt || this.fighters.length === 0) return;

        this.fighters.forEach((f, i) => {
            const out = document.getElementById(`response-${i}`);
            out.innerHTML = `<span class="streaming-pulse">INTERROGATING_${f.name.toUpperCase()}...</span>`;
            // DISPATCH: Send to Node 2 Auditor via Node 1 Proxy
        });
    }

    cycleMood() { this.assets.cycle(); }

    resetMatchmaker() {
        const flow = ['provider', 'type', 'tier', 'model'];
        flow.forEach(f => {
            const step = document.getElementById(`step-${f}`);
            const select = document.getElementById(`pick-${f}`);
            step.classList.remove('confirmed', 'active');
            select.classList.remove('selection-glow');
            select.value = "";
        });
        document.getElementById('step-provider').classList.add('active');
        document.getElementById('add-btn').disabled = true;
        document.getElementById('add-btn').style = "";
        this.matchmaker.reset();
        this.populate('provider');
    }
}