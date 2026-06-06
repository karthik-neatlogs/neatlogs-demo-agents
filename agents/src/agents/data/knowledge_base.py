"""Seed knowledge base for the Pinecone RAG demo.

A fictional product — "Lumio" smart desk lamp — so there is enough realistic
content to embed, retrieve, and answer questions over. Each entry is one
document that gets embedded (text-embedding-3-small, 1536 dims) and upserted
into the `neatlogs-testing` index.
"""

DOCUMENTS = [
    {
        "id": "kb-001",
        "title": "What is Lumio?",
        "text": (
            "Lumio is a smart desk lamp designed for focus and eye comfort. It "
            "pairs adjustable warm-to-cool lighting (2700K to 6500K) with an "
            "ambient light sensor that automatically tunes brightness to the "
            "room. Lumio connects over Wi-Fi and Bluetooth and is controlled by "
            "touch, the Lumio mobile app, or voice assistants. The lamp ships in "
            "Graphite, Sand, and Sage finishes and is rated for 50,000 hours of "
            "LED life."
        ),
    },
    {
        "id": "kb-002",
        "title": "Setting up Lumio for the first time",
        "text": (
            "To set up Lumio, plug in the USB-C power adapter and wait for the "
            "base ring to pulse white. Open the Lumio app, tap 'Add Device', and "
            "follow the prompts to join your 2.4GHz Wi-Fi network. Lumio does not "
            "support 5GHz networks during setup. If the ring pulses red, the lamp "
            "could not reach the network — move it closer to the router and try "
            "again. First-time setup usually completes in under two minutes."
        ),
    },
    {
        "id": "kb-003",
        "title": "Adjusting brightness and color temperature",
        "text": (
            "Tap and hold the top touch bar to cycle brightness from 1% to 100%. "
            "Swipe left or right on the bar to shift color temperature between "
            "warm (2700K) and cool (6500K). In the app, you can save up to four "
            "custom presets such as 'Reading', 'Focus', 'Relax', and 'Video "
            "Call'. Auto mode uses the ambient sensor to keep perceived "
            "brightness steady as daylight changes throughout the day."
        ),
    },
    {
        "id": "kb-004",
        "title": "Lumio battery and power",
        "text": (
            "The Lumio Pro model includes a built-in 4000mAh battery that lasts "
            "up to six hours at 50% brightness on a single charge. The standard "
            "Lumio model is powered directly by USB-C and has no internal "
            "battery. A full charge on the Pro takes about three hours. The base "
            "ring glows amber while charging and green when fully charged. "
            "Battery health is shown in the app under Device > Power."
        ),
    },
    {
        "id": "kb-005",
        "title": "Voice assistant and smart home support",
        "text": (
            "Lumio works with Amazon Alexa, Google Assistant, and Apple Home. "
            "After linking your account in the app, you can say things like "
            "'set the desk lamp to focus mode' or 'dim the lamp to 30 percent'. "
            "Lumio also supports Matter over Wi-Fi, so it can join most modern "
            "smart home hubs without an extra bridge. Routines and schedules can "
            "be configured either in the Lumio app or in your assistant's app."
        ),
    },
    {
        "id": "kb-006",
        "title": "Firmware updates",
        "text": (
            "Lumio checks for firmware updates automatically once a day and "
            "installs them overnight when the lamp is idle. You can also update "
            "manually from Settings > Firmware in the app. Do not unplug the lamp "
            "while the base ring is pulsing blue, which indicates an update is in "
            "progress. A typical update takes three to five minutes. If an update "
            "fails, the lamp rolls back to the previous version automatically."
        ),
    },
    {
        "id": "kb-007",
        "title": "Troubleshooting: Lumio won't turn on",
        "text": (
            "If Lumio does not turn on, first confirm the USB-C cable is fully "
            "seated in both the lamp and the adapter. Try a different power "
            "outlet and, if possible, a different USB-C cable rated for at least "
            "30W. Press and hold the touch bar for ten seconds to force a "
            "restart. If the base ring still shows no light, the power adapter "
            "may be faulty — contact support for a replacement under warranty."
        ),
    },
    {
        "id": "kb-008",
        "title": "Troubleshooting: Wi-Fi keeps disconnecting",
        "text": (
            "Frequent Wi-Fi drops are usually caused by a weak signal or router "
            "congestion. Keep Lumio within 10 meters of the router and away from "
            "microwaves and cordless phones. Make sure the lamp is on the 2.4GHz "
            "band, not 5GHz. In the app, go to Settings > Network > Reconnect to "
            "rejoin. If problems persist, reboot the router and perform a network "
            "reset on the lamp by holding the touch bar for twenty seconds."
        ),
    },
    {
        "id": "kb-009",
        "title": "Warranty and returns",
        "text": (
            "Every Lumio lamp includes a two-year limited warranty covering "
            "manufacturing defects. Accidental damage is not covered. You may "
            "return an unused Lumio within 30 days of purchase for a full refund. "
            "To start a return or warranty claim, open the app and go to Help > "
            "Warranty, or email support with your order number. Approved "
            "warranty replacements ship within five business days."
        ),
    },
    {
        "id": "kb-010",
        "title": "Cleaning and care",
        "text": (
            "Wipe the Lumio shade and base with a soft, dry microfiber cloth. Do "
            "not use water, alcohol, or abrasive cleaners, which can damage the "
            "matte finish and the touch bar. Keep the ambient light sensor on "
            "the front of the base free of dust so auto-brightness stays "
            "accurate. The lamp is not water resistant and should be kept away "
            "from sinks, windowsills, and other damp areas."
        ),
    },
    {
        "id": "kb-011",
        "title": "Lumio subscription and app features",
        "text": (
            "The Lumio app is free and covers all core controls. Lumio+ is an "
            "optional subscription at $3 per month that adds circadian lighting "
            "schedules, usage analytics, focus-session tracking, and early "
            "access to new presets. Lumio+ is not required to use the lamp. You "
            "can start a 14-day free trial from the app, and you can cancel "
            "anytime from your account settings without losing core features."
        ),
    },
    {
        "id": "kb-012",
        "title": "Privacy and data",
        "text": (
            "Lumio collects device telemetry such as brightness levels, firmware "
            "version, and connection status to improve reliability. The lamp does "
            "not contain a camera or microphone. Voice commands are processed by "
            "your chosen assistant, not by Lumio. You can export or delete your "
            "account data at any time from Settings > Privacy. Telemetry sharing "
            "can be turned off, though this disables usage analytics in Lumio+."
        ),
    },
]
