# Brick 

Hi! This is a compilation for workers/automations to help me with things. Currently, i have a **pritinting worker**

## How to run?

1. Clone this
`git clone https://github.com/afonsoingles/brick-core`
2. Run UV
`uv sync`
3. Set the envs!
You can use doppler by setting up a `DOPPLER_TOKEN` or use env variables directly.
Here are the necessary ones:
```
ENV=development
MAILGUN_API_KEY=key
MAILGUN_DOMAIN=example.com
PRINTER_CUPS_HOST=192.168.X.X
PRINTER_CUPS_PORT=631
PRINTER_CUPS_NAME=Your_Printer_Name
PRINTER_EMAIL=printer@example.com
SECURE_KEY=secure_key123
```
4. Run it!
`uvicorn main:app --reload --host 0.0.0.0`

That's it!

### Printer
This is (currently) the only worker. It forwards emails sent to my printer's email to my actual printer, so its files are actually printed.
