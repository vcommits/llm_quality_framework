/**
 * ArenaUI Class
 *
 * Manages the user interface for the Arena Matchmaker, following the OOP-GLASSDESK architecture.
 * It handles the "Postman Foldout," "Bloom Effect," and other UI interactions.
 */
class ArenaUI {
    constructor() {
        // Cache DOM elements here
        this.postmanFoldout = document.getElementById('postman-foldout');
        this.providerSelect = document.getElementById('provider-select');
        this.typeSelect = document.getElementById('type-select');
        this.tierSelect = document.getElementById('tier-select');
        this.modelSelect = document.getElementById('model-select');
    }

    /**
     * Initializes the UI, setting up initial states and event listeners.
     */
    initialize() {
        this.closePostman(); // Start with it closed
        this.disableBloomableSections();
        this.setupEventListeners();
    }

    /**
     * Sets up all necessary event listeners for the UI.
     */
    setupEventListeners() {
        // Example: document.getElementById('open-button').addEventListener('click', () => this.openPostman());
    }

    openPostman() {
        this.postmanFoldout.style.transform = 'translateX(0)';
    }

    closePostman() {
        this.postmanFoldout.style.transform = 'translateX(-400px)';
    }

    /**
     * Disables and fades out sections that "bloom."
     */
    disableBloomableSections() {
        this.typeSelect.style.opacity = '0.15';
        this.typeSelect.disabled = true;
        this.tierSelect.style.opacity = '0.15';
        this.tierSelect.disabled = true;
        this.modelSelect.style.opacity = '0.15';
        this.modelSelect.disabled = true;
    }

    /**
     * "Blooms" a UI section into view.
     * @param {HTMLElement} element The UI element to bloom.
     */
    bloom(element) {
        element.style.opacity = '1';
        element.disabled = false;
        this.pulseGreen(element);
    }

    /**
     * Pulses an element with the green affirmation color.
     * @param {HTMLElement} element
     */
    pulseGreen(element) {
        element.style.transition = 'box-shadow 200ms ease-in';
        element.style.boxShadow = '0 0 10px 3px #00ff41';
        setTimeout(() => {
            element.style.boxShadow = 'none';
        }, 200);
    }

    /**
     * Simulates a shredder animation for removing an item.
     * @param {HTMLElement} cardElement The card to be "shredded."
     */
    shred(cardElement) {
        cardElement.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
        cardElement.style.transform = 'translateY(100%) scale(0.1)';
        cardElement.style.opacity = '0';
        // In a real app, you'd remove the element from the DOM after the animation
        setTimeout(() => cardElement.remove(), 500);
    }
}
