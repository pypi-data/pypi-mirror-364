import random
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Suspect:
    name: str
    footprints: bool  # 足迹匹配
    fingerprints: bool  # 指纹匹配
    dna: bool  # DNA匹配
    description: str  # 嫌疑人描述
    suspicious_level: int  # 可疑度(1-5)

class Game:
    def __init__(self):
        self.suspects: List[Suspect] = []
        self.current_suspect = None
        self.selected_suspect = None
        self.nausea_level = 0  # 孕吐值
        self.generate_suspects()
        
    def generate_suspects(self):
        """生成3-6个随机嫌疑人，其中一个是真正的拉屎者"""
        names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十", "郑十一", "王十二"]
        random.shuffle(names)
        num_suspects = random.randint(3, 6)
        
        # 随机选择一个作为真正的拉屎者
        culprit_index = random.randint(0, num_suspects-1)
        
        for i in range(num_suspects):
            is_culprit = (i == culprit_index)
            # 随机生成可疑度(1-5)
            suspicious_level = random.randint(1, 5)
            if is_culprit:
                suspicious_level = max(3, suspicious_level)  # 真凶至少3级可疑
                
            # 确保真凶有所有三种线索
            if is_culprit:
                self.suspects.append(Suspect(
                    name=names[i],
                    footprints=True,
                    fingerprints=True,
                    dna=True,
                    description=self.generate_description(names[i], True, suspicious_level),
                    suspicious_level=suspicious_level
                ))
            else:
                # 非真凶随机生成0-2种线索
                clue_count = random.randint(0, 2)
                clues = random.sample(['footprints', 'fingerprints', 'dna'], clue_count)
                
                self.suspects.append(Suspect(
                    name=names[i],
                    footprints='footprints' in clues,
                    fingerprints='fingerprints' in clues,
                    dna='dna' in clues,
                    description=self.generate_description(names[i], False, suspicious_level),
                    suspicious_level=suspicious_level
                ))
    
    def generate_description(self, name: str, is_culprit: bool, suspicious_level: int) -> str:
        """生成嫌疑人描述"""
        level_desc = {
            1: "看起来完全无辜",
            2: "有点可疑",
            3: "相当可疑",
            4: "非常可疑",
            5: "极度可疑"
        }
        
        if is_culprit:
            return f"{name}最近肠胃不好，经常跑厕所 - {level_desc[suspicious_level]}"
        else:
            reasons = [
                "刚刚去过厕所但只是小便",
                "声称自己今天还没上过厕所",
                "有不在场证明",
                "最近便秘"
            ]
            return f"{name}{random.choice(reasons)} - {level_desc[suspicious_level]}"
    
    def check_clues(self) -> Dict[str, bool]:
        """检查当前线索状态"""
        if not self.current_suspect:
            return {}
            
        return {
            "footprints": self.current_suspect.footprints,
            "fingerprints": self.current_suspect.fingerprints,
            "dna": self.current_suspect.dna
        }
    
    def increase_nausea(self, amount: int = 1):
        """增加孕吐值"""
        self.nausea_level += amount
        if self.nausea_level >= 10:
            print("警告：孕吐太厉害，游戏结束！")
            # TODO: 实现游戏结束逻辑
