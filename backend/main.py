from app.services.spreadsheet_parser import SpreadsheetHandler
from app.services.answer_generator import Generator
from app.services.ppt_generator import PresentationGenerator
import pandas
import asyncio

async def main():
    handler = SpreadsheetHandler("test")
    llm = Generator()

    questions = handler.extract_questions()
    qlist = questions["Questions"].to_list()

    tasks = [llm.generate_response(question) for question in questions['Questions']]
    responses = await asyncio.gather(*tasks) # list of dicts {"Answer": ans}

    handler.write_to_sheet(responses)

    # PPT Agent's step
    data = pack_data(qlist, responses)
    gen_ppt(data)

def gen_ppt(content):
    pgen = PresentationGenerator("output")
    for i in content:
        pgen.add_slide(1, 20)
        pgen.add_content(i)
        pgen.save_presentation()

def pack_data(qlist, responses):
    # doing the agents job for now, basically returns a list of dicts {"Title": w/e, "Content": w/e}
    data = []
    for i in range(len(responses)):
        data.append({"Title": qlist[i], "Content": responses[i]["Answer"]})
    return data

if __name__ == "__main__":
    asyncio.run(main())
