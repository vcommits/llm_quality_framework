from pytest_bdd import given, when, then, parsers
from utils.payload_catalog import get_base_payload
from utils.payload_modifiers import apply_modifiers


@when(parsers.parse('I load the base payload "{payload_name}" from "{category}"'))
def load_payload(context, payload_name, category):
    # Reaches into payload_catalog.py
    context.current_payload = get_base_payload(category, payload_name)


@when(parsers.parse('I apply the payload modifiers: "{modifier_list}"'))
def mutate_payload(context, modifier_list):
    # Parses the comma-separated list and reaches into payload_modifiers.py
    modifiers = [m.strip() for m in modifier_list.split(',')]
    context.mutated_payload = apply_modifiers(context.current_payload, modifiers)


@when(parsers.parse('I inject the mutated payload into the hidden DOM layer of "{url}"'))
async def inject_into_dom(context, url):
    # Playwright dynamically creates a hidden <div> and drops the mutated payload into it
    await context.page.goto(url)

    await context.page.evaluate(f"""
        const trap = document.createElement('div');
        trap.style.opacity = '0.01';
        trap.innerText = `{context.mutated_payload}`;
        document.body.appendChild(trap);
    """)

    # Trigger the agent to read the page...