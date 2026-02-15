# Brick 

Hi! This is a compilation for workers/automations to help me with things. Currently, i have a **pritinting worker**

## How to run?

1. Clone this
`git clone https://github.com/afonsoingles/brick-core`
2. Run UV
`uv sync`
3. Set the envs!
You can use doppler by setting up a `DOPPLER_TOKEN` or use env variables directly.
You can check the necessary env variables in the `.env.example` file.
4. Run it!
`uvicorn main:app --reload --host 0.0.0.0`

That's it!

### Printer
This is (currently) the only worker. It forwards emails sent to my printer's email to my actual printer, so its files are actually printed. With the new authentication system, i will be adding the ability to see wich files you sent to the printer, via the Brick Dashboard.
