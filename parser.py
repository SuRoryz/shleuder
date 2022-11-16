import textract as tx
from striprtf.striprtf import rtf_to_text
import re

class Parser():
    def __init__(self):
        self.parsers = {
            "Препод": [ParserType1.parseTeacherName, ParserType2.parseTeacherName],
            "Группы": [ParserType1.parseTeacherShleude, ParserType2.parseTeacherShleude,]
        }

        self.current_teacher = None
        self.with_date = False
        self.with_week = False
        
        self.shleude = {}

    def parse(self, path, *args, **kwargs) -> dict:
        if ".rtf" in path:
            with open(path, 'r') as f:
                text = list(map(lambda x: x.strip(" "), filter(lambda x: len(x) != 0, rtf_to_text(f.read(), errors='ignore').split("\n"))))
        else:
            text = list(map(lambda x: x.strip(" "), filter(lambda x: len(x) != 0, tx.process(path).decode("UTF-8").split("\n"))))

        type_ = 0
        if 'И З В Е Щ Е Н И Е' in text[0]:
            type_ = 1

        for index, item in enumerate(text):
            if "Дата" in item:
                self.with_date = True
            if "ЧЁТНАЯ" in item:
                self.with_week = True

            if "И З В Е Щ Е Н И Е" in item:
                t = "Препод"
            elif "группы" in item:
                t = "Группы"
            else:
                continue

            try:
                self.parsers[t][type_](index, item, text, self.shleude , self)
            except:
                try:
                    self.parsers[t][type_](index-1, item, text, self.shleude, self)
                except:
                    pass

class ParserType2():
    @staticmethod
    def parseTeacherName(index, item, text, result_dict, mainClass):
            _splitted = list(map(lambda x: x.strip(), filter(lambda x: len(x) != 0, item.split("  "))))

            mainClass.current_teacher = _splitted[_splitted.index("И З В Е Щ Е Н И Е")+1]
            result_dict[mainClass.current_teacher] = {"Нечётная неделя": [], "Чётная неделя": []}

    @staticmethod
    def parseTeacherShleude(index, item, text, result_dict, mainClass):
        skip = False
        is_n = False

        try:
            for i, line in enumerate(text[index+1:]):
                if "(!)" in line or "И З В Е Щ Е Н И Е" in line:
                    break
                if "--" in line or len(line) <= 1 or skip:
                    skip = False
                    continue
                if mainClass.with_week:
                    if "ЧЕТНАЯ" in line:
                        is_n = True
                        continue

                    n = "Чётная неделя" if is_n else "Нечётная неделя"
                    is_n = False
                else:
                    n = "Нечётная неделя"
                
                line = list(filter(lambda x: len(x) >= 1, map(lambda x: x.strip(), line.split("¦"))))

                if mainClass.with_date:
                    result_dict[mainClass.current_teacher][n].append({"Название": line[0],
                                                        "Дата": line[1],
                                                        "День недели": line[2],
                                                        "Время": line[3],
                                                        "Аудитория": line[4],
                                                        "Группы": line[5].split(",")})
                else:
                    result_dict[mainClass.current_teacher][n].append({"Название": line[0],
                                                        "День недели": line[1],
                                                        "Время": line[2],
                                                        "Аудитория": line[3],
                                                        "Группы": line[4].split(",")})
                skip = True
        except:
            pass
    
class ParserType1():
    @staticmethod
    def parseTeacherName(index, item, text, result_dict, mainClass):
        mainClass.current_teacher = re.match(r".+\D\.\D\.", text[index-1])[0]
        result_dict[mainClass.current_teacher] = {"Любая неделя": []}
    
    @staticmethod
    def parseTeacherShleude(index, item, text, result_dict, mainClass):
        skip = False

        try:
            for i, line in enumerate(text[index+1:]):
                if "(!)" in line or "И З В Е Щ Е Н И Е" in line:
                    break
                if "--" in line or len(line) <= 1 or skip:
                    skip = False
                    continue
                
                line = list(filter(lambda x: len(x) >= 1, map(lambda x: x.strip(), line.split("¦"))))
                result_dict[mainClass.current_teacher]["Любая неделя"].append({"Название": line[0],
                                                    "Дата": line[1],
                                                    "День недели": line[2],
                                                    "Время": line[3],
                                                    "Аудитория": line[4],
                                                    "Группы": text[index+2+i].replace("¦", "").strip().split(",")})
                skip = True
        except:
            pass

#c = Parser()
#c.parse("primer3.doc")
