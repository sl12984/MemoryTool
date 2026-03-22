import tkinter as tk
from tkinter import messagebox
import random
from collections import Counter
import sys
import os

# 牌的定义和排序
CARD_ORDER = {'D': 0, 'X': 1, '2': 2, 'A': 3, 'K': 4, 'Q': 5, 'J': 6, 'T': 7,
              '9': 8, '8': 9, '7': 10, '6': 11, '5': 12, '4': 13, '3': 14}


def create_deck():
    """创建一副完整的牌"""
    deck = ['D', 'X']
    for card in ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']:
        deck.extend([card] * 4)
    return deck


def sort_cards(cards):
    """按照牌的大小排序"""
    return sorted(cards, key=lambda x: CARD_ORDER[x])


def is_valid_combination(cards):
    """检查是否是有效的牌型"""
    if not cards:
        return False

    card_count = Counter(cards)
    counts = sorted(card_count.values(), reverse=True)
    counts_str = ','.join(map(str, sorted(counts)))

    if len(cards) == 1:
        return "single"
    if len(cards) == 2 and counts_str == "2":
        return "pair"
    if len(cards) == 4 and counts_str == "1,3":
        return "triple_one"
    if len(cards) == 5 and counts_str == "2,3":
        return "triple_two"
    if set(cards) == {'D', 'X'}:
        return "rocket"

    # 顺子
    if len(cards) >= 5:
        sorted_cards = sorted(set(cards), key=lambda x: CARD_ORDER[x])
        consecutive = True
        for i in range(len(sorted_cards) - 1):
            if CARD_ORDER[sorted_cards[i + 1]] - CARD_ORDER[sorted_cards[i]] != 1:
                consecutive = False
                break

        if consecutive and '2' not in cards and 'D' not in cards and 'X' not in cards:
            if all(card_count[card] == 1 for card in sorted_cards):
                return "straight"

    # 连对
    if len(cards) >= 6 and len(cards) % 2 == 0:
        pairs = [card for card, count in card_count.items() if count == 2]
        if len(pairs) == len(cards) // 2:
            sorted_pairs = sorted(pairs, key=lambda x: CARD_ORDER[x])
            consecutive = True
            for i in range(len(sorted_pairs) - 1):
                if CARD_ORDER[sorted_pairs[i + 1]] - CARD_ORDER[sorted_pairs[i]] != 1:
                    consecutive = False
                    break

            if consecutive and '2' not in pairs and 'D' not in pairs and 'X' not in pairs:
                return "pair_straight"

    return False


# 牌型权重
HAND_TYPE_WEIGHTS = {
    "single": 5,
    "pair": 3,
    "triple_one": 2,
    "triple_two": 1,
    "straight": 1,
    "pair_straight": 1,
    "rocket": 0
}


def get_random_hand_type():
    """按权重随机选择牌型类别"""
    types = []
    weights = []

    for hand_type, weight in HAND_TYPE_WEIGHTS.items():
        if weight > 0:
            types.append(hand_type)
            weights.append(weight)

    return random.choices(types, weights=weights, k=1)[0]


def generate_single(available_cards):
    """生成单张"""
    return [random.choice(available_cards)]


def generate_pair(available_cards):
    """生成对子"""
    card_counts = Counter(available_cards)
    pairs = [card for card, count in card_counts.items() if count >= 2]
    if pairs:
        selected = random.choice(pairs)
        return [selected, selected]
    return None


def generate_triple_one(available_cards):
    """生成三带一"""
    card_counts = Counter(available_cards)
    triples = [card for card, count in card_counts.items() if count >= 3]
    if triples:
        triple_card = random.choice(triples)
        remaining_cards = [card for card in available_cards if card != triple_card]
        if remaining_cards:
            single_card = random.choice(remaining_cards)
            return [triple_card, triple_card, triple_card, single_card]
    return None


def generate_triple_two(available_cards):
    """生成三带二"""
    card_counts = Counter(available_cards)
    triples = [card for card, count in card_counts.items() if count >= 3]
    if triples:
        triple_card = random.choice(triples)
        card_counts[triple_card] -= 3

        pairs = [card for card, count in card_counts.items() if count >= 2]
        if pairs:
            pair_card = random.choice(pairs)
            return [triple_card, triple_card, triple_card, pair_card, pair_card]
    return None


def generate_straight(available_cards):
    """生成顺子"""
    straight_cards = [card for card in available_cards if card not in ['2', 'D', 'X']]
    card_counts = Counter(straight_cards)

    available_unique = sorted([card for card, count in card_counts.items() if count >= 1],
                              key=lambda x: CARD_ORDER[x])

    if len(available_unique) >= 5:
        for start_idx in range(len(available_unique) - 4):
            consecutive_cards = []
            current_card = available_unique[start_idx]

            for i in range(len(available_unique) - start_idx):
                next_card = available_unique[start_idx + i]
                if CARD_ORDER[next_card] - CARD_ORDER[current_card] == i:
                    consecutive_cards.append(next_card)
                else:
                    break

            if len(consecutive_cards) >= 5:
                max_length = min(len(consecutive_cards), 12)
                if max_length >= 5:
                    length = random.randint(5, max_length)
                    return consecutive_cards[:length]

    return None


def generate_pair_straight(available_cards):
    """生成连对"""
    straight_cards = [card for card in available_cards if card not in ['2', 'D', 'X']]
    card_counts = Counter(straight_cards)

    available_pairs = sorted([card for card, count in card_counts.items() if count >= 2],
                             key=lambda x: CARD_ORDER[x])

    if len(available_pairs) >= 3:
        for start_idx in range(len(available_pairs) - 2):
            consecutive_pairs = []
            current_card = available_pairs[start_idx]

            for i in range(len(available_pairs) - start_idx):
                next_card = available_pairs[start_idx + i]
                if CARD_ORDER[next_card] - CARD_ORDER[current_card] == i:
                    consecutive_pairs.append(next_card)
                else:
                    break

            if len(consecutive_pairs) >= 3:
                max_length = min(len(consecutive_pairs), 10)
                if max_length >= 3:
                    length = random.randint(3, max_length)
                    result = []
                    for card in consecutive_pairs[:length]:
                        result.extend([card, card])
                    return result

    return None


def generate_rocket(available_cards):
    """生成王炸"""
    if 'D' in available_cards and 'X' in available_cards:
        return ['D', 'X']
    return None


# 牌型生成函数映射
HAND_GENERATORS = {
    "single": generate_single,
    "pair": generate_pair,
    "triple_one": generate_triple_one,
    "triple_two": generate_triple_two,
    "straight": generate_straight,
    "pair_straight": generate_pair_straight,
    "rocket": generate_rocket
}


def generate_valid_hands(deck, player_cards, num_hands=10):
    """生成指定数量的有效牌型"""
    hands = []
    attempts = 0

    while len(hands) < num_hands and attempts < 5000:
        attempts += 1

        current_card_count = Counter(player_cards)
        for hand in hands:
            current_card_count.update(Counter(hand))

        available_cards = []
        for card in deck:
            if card in ['D', 'X']:
                max_count = 1
            else:
                max_count = 4

            current_count = current_card_count.get(card, 0)
            remaining_count = max_count - current_count

            for _ in range(remaining_count):
                available_cards.append(card)

        if len(available_cards) == 0:
            break

        hand_type = get_random_hand_type()
        hand_generator = HAND_GENERATORS[hand_type]
        potential_hand = hand_generator(available_cards)

        if potential_hand is not None:
            temp_card_count = current_card_count.copy()
            temp_card_count.update(Counter(potential_hand))

            valid_count = True
            for card, count in temp_card_count.items():
                if card in ['D', 'X']:
                    if count > 1:
                        valid_count = False
                        break
                else:
                    if count > 4:
                        valid_count = False
                        break

            if valid_count:
                hands.append(potential_hand)

    # 补充单张
    while len(hands) < num_hands:
        current_card_count = Counter(player_cards)
        for hand in hands:
            current_card_count.update(Counter(hand))

        available_cards = []
        for card in deck:
            if card in ['D', 'X']:
                max_count = 1
            else:
                max_count = 4

            current_count = current_card_count.get(card, 0)
            remaining_count = max_count - current_count

            for _ in range(remaining_count):
                available_cards.append(card)

        if len(available_cards) > 0:
            hands.append([random.choice(available_cards)])
        else:
            break

    return hands


class MemoryGameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("记忆训练游戏")
        self.root.geometry("900x700")

        # 游戏配置
        self.display_time = 0
        self.num_hands = 10

        # 游戏状态
        self.current_phase = "launcher"  # launcher, difficulty, game
        self.game_phase = "display"  # display, quiz_duan, quiz_count

        # 游戏数据
        self.deck = None
        self.player_cards = None
        self.hands = None
        self.current_hand_index = 0
        self.is_showing = False
        self.used_card_count = None
        self.remaining_card_count = None
        self.duan_cards = None

        # 评分系统
        self.total_score = 0
        self.correct_count = 0
        self.total_questions = 0

        # 测验变量
        self.duan_selected = set()
        self.current_count_question = 0
        self.count_questions_order = ['D', 'X', '2', 'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3']

        # 创建所有界面
        self.create_launcher_interface()
        self.create_difficulty_interface()
        self.create_game_interface()

        # 显示启动界面
        self.show_launcher()

        # 窗口居中
        self.center_window()

    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.root.winfo_width()) // 2
        y = (screen_height - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")

    def clear_all_frames(self):
        """隐藏所有界面"""
        self.launcher_frame.pack_forget()
        self.difficulty_frame.pack_forget()
        self.game_frame.pack_forget()

    # ==================== 启动界面 ====================
    def create_launcher_interface(self):
        """创建启动界面"""
        self.launcher_frame = tk.Frame(self.root)

        # 顶部标题
        title_label = tk.Label(
            self.launcher_frame,
            text="记忆训练",
            font=("Microsoft YaHei", 24, "bold")
        )
        title_label.pack(pady=80)

        # 开始按钮
        start_button = tk.Button(
            self.launcher_frame,
            text="开始",
            command=self.show_difficulty,
            font=("Microsoft YaHei", 16),
            width=12,
            height=2,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            cursor="hand2"
        )
        start_button.pack(pady=30)

        # 说明
        info_label = tk.Label(
            self.launcher_frame,
            text="斗地主记忆训练游戏\n提高你的记忆力和牌感",
            font=("Microsoft YaHei", 10),
            fg="gray"
        )
        info_label.pack(pady=20)

    def show_launcher(self):
        """显示启动界面"""
        self.clear_all_frames()
        self.launcher_frame.pack(fill=tk.BOTH, expand=True)

    # ==================== 难度选择界面 ====================
    def create_difficulty_interface(self):
        """创建难度选择界面"""
        self.difficulty_frame = tk.Frame(self.root)

        # 返回按钮
        back_button = tk.Button(
            self.difficulty_frame,
            text="← 返回",
            command=self.show_launcher,
            font=("Microsoft YaHei", 10),
            bg="#DDDDDD",
            fg="black",
            cursor="hand2"
        )
        back_button.place(x=10, y=10)

        # 顶部标题
        title_label = tk.Label(
            self.difficulty_frame,
            text="难度选择",
            font=("Microsoft YaHei", 24, "bold")
        )
        title_label.pack(pady=60)

        # 输入框框架
        input_frame = tk.Frame(self.difficulty_frame)
        input_frame.pack(pady=15)

        # 标签
        label = tk.Label(input_frame, text="一手存留的秒数：", font=("Microsoft YaHei", 14))
        label.pack(side=tk.LEFT, padx=10)

        # 输入框
        self.time_entry = tk.Entry(input_frame, font=("Microsoft YaHei", 14), width=15)
        self.time_entry.pack(side=tk.LEFT)
        self.time_entry.insert(0, "0")

        # 说明文字
        info_label = tk.Label(
            self.difficulty_frame,
            text="输入 0 表示手动控制（点击空白处显示下一手）",
            font=("Microsoft YaHei", 11),
            fg="gray"
        )
        info_label.pack(pady=5)

        # 手数输入框框架
        hand_frame = tk.Frame(self.difficulty_frame)
        hand_frame.pack(pady=15)

        # 手数标签
        hand_label = tk.Label(hand_frame, text="手数（1-20）：", font=("Microsoft YaHei", 14))
        hand_label.pack(side=tk.LEFT, padx=10)

        # 手数输入框
        self.hand_entry = tk.Entry(hand_frame, font=("Microsoft YaHei", 14), width=15)
        self.hand_entry.pack(side=tk.LEFT)
        self.hand_entry.insert(0, "10")

        # 开始按钮
        start_button = tk.Button(
            self.difficulty_frame,
            text="开始记忆",
            command=self.start_game,
            font=("Microsoft YaHei", 16),
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            cursor="hand2"
        )
        start_button.pack(pady=40)

    def show_difficulty(self):
        """显示难度选择界面"""
        self.clear_all_frames()
        self.difficulty_frame.pack(fill=tk.BOTH, expand=True)

    def start_game(self):
        """开始游戏"""
        time_str = self.time_entry.get().strip()
        hand_str = self.hand_entry.get().strip()

        if not time_str:
            messagebox.showwarning("提示", "请输入显示秒数")
            return

        if not hand_str:
            messagebox.showwarning("提示", "请输入手数")
            return

        try:
            self.display_time = int(time_str)
            if self.display_time < 0:
                messagebox.showwarning("提示", "秒数不能为负数")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的数字")
            return

        try:
            self.num_hands = int(hand_str)
            if self.num_hands < 1 or self.num_hands > 20:
                messagebox.showwarning("提示", "手数必须在1-20之间")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的手数")
            return

        # 初始化游戏
        self.initialize_game()
        self.show_game()

    # ==================== 游戏界面 ====================
    def initialize_game(self):
        """初始化游戏数据"""
        # 创建牌组
        self.deck = create_deck()

        # 给玩家发牌
        self.player_hand_size = random.choice([17, 20])
        self.player_cards = sort_cards(random.sample(self.deck, self.player_hand_size))

        # 生成手牌
        self.hands = generate_valid_hands(self.deck, self.player_cards, self.num_hands)

        # 重置游戏状态
        self.current_hand_index = 0
        self.is_showing = False
        self.game_phase = "display"
        self.total_score = 0
        self.correct_count = 0
        self.total_questions = 0
        self.duan_selected = set()
        self.current_count_question = 0

        # 计算剩余牌
        self.calculate_remaining_cards()

    def calculate_remaining_cards(self):
        """计算剩余牌的数量"""
        self.used_card_count = Counter(self.player_cards)
        for hand in self.hands:
            self.used_card_count.update(Counter(hand))

        self.total_card_count = Counter()
        self.total_card_count.update(['D', 'X'])
        for card in ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']:
            self.total_card_count.update([card] * 4)

        self.remaining_card_count = Counter()
        for card in self.total_card_count:
            self.remaining_card_count[card] = self.total_card_count[card] - self.used_card_count.get(card, 0)

        self.duan_cards = []
        normal_cards = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        for card in normal_cards:
            if self.used_card_count.get(card, 0) == 0:
                self.duan_cards.append(card)

    def create_game_interface(self):
        """创建游戏界面"""
        self.game_frame = tk.Frame(self.root)

        # 返回按钮
        back_button = tk.Button(
            self.game_frame,
            text="← 返回",
            command=self.show_difficulty,
            font=("Microsoft YaHei", 10),
            bg="#DDDDDD",
            fg="black",
            cursor="hand2"
        )
        back_button.place(x=10, y=10)

        # 玩家手牌显示
        player_frame = tk.Frame(self.game_frame)
        player_frame.place(x=50, y=50)

        player_label = tk.Label(
            player_frame,
            text="你的手牌：",
            font=("Microsoft YaHei", 12, "bold")
        )
        player_label.pack()

        self.player_cards_label = tk.Label(
            player_frame,
            text="",
            font=("Courier New", 14, "bold"),
            fg="blue"
        )
        self.player_cards_label.pack()

        # 显示区域
        display_frame = tk.Frame(self.game_frame)
        display_frame.place(x=50, y=150)

        self.display_label = tk.Label(
            display_frame,
            text="显示的牌：",
            font=("Microsoft YaHei", 12, "bold")
        )
        self.display_label.pack()

        self.display_cards_label = tk.Label(
            display_frame,
            text="",
            font=("Courier New", 18, "bold"),
            fg="red",
            wraplength=800
        )
        self.display_cards_label.pack(pady=20)

        # 进度显示
        self.progress_label = tk.Label(
            self.game_frame,
            text="",
            font=("Microsoft YaHei", 12)
        )
        self.progress_label.place(x=50, y=250)

        # 模式提示
        self.mode_label = tk.Label(
            self.game_frame,
            text="",
            font=("Microsoft YaHei", 10),
            fg="gray"
        )
        self.mode_label.place(x=50, y=280)

        # 测验区域
        self.quiz_frame = tk.Frame(self.game_frame)

        # 断张测验
        self.duan_frame = tk.Frame(self.quiz_frame)

        duan_question = tk.Label(
            self.duan_frame,
            text="断张还有哪些？（不包括D和X，多选）",
            font=("Microsoft YaHei", 14, "bold")
        )
        duan_question.pack(pady=10)

        self.duan_options_frame = tk.Frame(self.duan_frame)
        self.duan_options_frame.pack(pady=10)

        self.duan_confirm_button = tk.Button(
            self.duan_frame,
            text="确认答案",
            command=self.check_duan_answer,
            font=("Microsoft YaHei", 12),
            width=15,
            height=1,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )

        # 数量测验
        self.count_frame = tk.Frame(self.quiz_frame)

        count_question = tk.Label(
            self.count_frame,
            text="外面还有多少张？",
            font=("Microsoft YaHei", 14, "bold")
        )
        count_question.pack(pady=10)

        self.current_card_label = tk.Label(
            self.count_frame,
            text="",
            font=("Microsoft YaHei", 16, "bold"),
            fg="blue"
        )
        self.current_card_label.pack(pady=5)

        self.count_options_frame = tk.Frame(self.count_frame)
        self.count_options_frame.pack(pady=10)

        self.answer_label = tk.Label(
            self.quiz_frame,
            text="",
            font=("Microsoft YaHei", 12, "bold")
        )
        self.answer_label.pack(pady=10)

        self.next_question_button = tk.Button(
            self.quiz_frame,
            text="下一题",
            command=self.next_question,
            font=("Microsoft YaHei", 12),
            width=15,
            height=1,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )

        # 绑定点击事件
        self.root.bind("<Button-1>", self.on_window_click)

    def show_game(self):
        """显示游戏界面"""
        self.clear_all_frames()
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        # 更新玩家手牌显示
        player_cards_text = " ".join(self.player_cards)
        self.player_cards_label.config(text=player_cards_text)

        # 更新模式显示
        mode_text = "自动模式" if self.display_time > 0 else "手动模式"
        self.mode_label.config(text=f"{mode_text} ({self.display_time}秒)")

        # 重置显示
        self.display_label.config(text="显示的牌：")
        self.display_cards_label.config(text="")
        self.progress_label.config(text=f"进度：0/{self.num_hands}")

        # 隐藏测验区域
        self.quiz_frame.place_forget()

        # 开始显示牌
        if self.display_time > 0:
            self.root.after(1000, self.auto_play)
        else:
            self.root.bind("<Button-1>", self.manual_next_hand)

    def manual_next_hand(self, event=None):
        """手动显示下一手牌"""
        if self.display_time > 0:  # 自动模式下不响应手动点击
            return

        if self.game_phase == "display":
            if self.current_hand_index < len(self.hands):
                if self.is_showing:
                    self.hide_hand()
                    self.is_showing = False
                    self.current_hand_index += 1
                else:
                    self.show_hand(self.current_hand_index)
                    self.is_showing = True

            if self.current_hand_index >= len(self.hands) and not self.is_showing:
                self.progress_label.config(text="训练完成！")
                self.start_quiz_phase()

    def show_hand(self, hand_index):
        """显示指定索引的牌"""
        try:
            # 检查 hands 是否有效
            if self.hands is None:
                print("错误：self.hands 为 None")
                return

            if not isinstance(self.hands, list):
                print(f"错误：self.hands 不是列表，类型: {type(self.hands)}")
                return

            if 0 <= hand_index < len(self.hands):
                hand = self.hands[hand_index]
                hand_text = " ".join(hand)
                self.display_cards_label.config(text=hand_text)
                self.progress_label.config(text=f"进度：{hand_index + 1}/{self.num_hands}")
            else:
                print(f"错误：手牌索引 {hand_index} 超出范围，总手牌数: {len(self.hands)}")
        except Exception as e:
            print(f"显示手牌时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def hide_hand(self):
        """隐藏当前牌"""
        self.display_cards_label.config(text="")

    def on_window_click(self, event):
        """窗口点击事件"""
        try:
            # 检查是否在游戏界面且游戏已经开始
            if self.current_phase != "game":
                return  # 不在游戏界面，直接返回

            if self.game_phase != "display":
                return  # 不在显示阶段，直接返回

            # 检查 hands 是否有效
            if self.hands is None:
                return  # 游戏数据未初始化，直接返回

            if self.display_time == 0 and self.game_phase == "display":
                if self.current_hand_index < len(self.hands):
                    if self.is_showing:
                        self.hide_hand()
                        self.is_showing = False
                        self.current_hand_index += 1
                    else:
                        self.show_hand(self.current_hand_index)
                        self.is_showing = True

                if self.current_hand_index >= len(self.hands) and not self.is_showing:
                    self.progress_label.config(text="训练完成！")
                    self.start_quiz_phase()
        except Exception as e:
            print(f"窗口点击事件出错: {str(e)}")

    def auto_play(self):
        """自动播放模式"""
        if self.display_time <= 0 or self.current_hand_index >= len(self.hands):
            if self.current_hand_index >= len(self.hands):
                self.progress_label.config(text="训练完成！")
                self.start_quiz_phase()
            return

        self.show_hand(self.current_hand_index)
        self.is_showing = True

        delay = self.display_time * 1000
        self.root.after(delay, self.auto_hide_and_next)

    def auto_hide_and_next(self):
        """自动隐藏并进入下一手"""
        if self.current_hand_index < len(self.hands):
            self.hide_hand()
            self.current_hand_index += 1
            self.is_showing = False

            if self.current_hand_index < len(self.hands):
                self.root.after(1000, self.auto_play)
            else:
                self.progress_label.config(text="训练完成！")
                self.start_quiz_phase()

    def start_quiz_phase(self):
        """开始测验阶段"""
        self.game_phase = "quiz_duan"
        self.display_label.config(text="")
        self.display_cards_label.config(text="")
        self.quiz_frame.place(x=50, y=300)
        self.show_duan_question()

    def show_duan_question(self):
        """显示断张测验"""
        self.count_frame.pack_forget()
        self.next_question_button.pack_forget()
        self.answer_label.config(text="")
        self.duan_frame.pack()

        # 清除之前的选项
        for widget in self.duan_options_frame.winfo_children():
            widget.destroy()

        self.duan_selected = set()

        # 创建选项
        options = ['2', 'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3']
        options.sort(key=lambda x: CARD_ORDER[x])

        for option in options:
            button = tk.Button(
                self.duan_options_frame,
                text=option,
                command=lambda c=option: self.toggle_duan_card(c),
                font=("Microsoft YaHei", 12),
                width=3,
                height=1,
                cursor="hand2"
            )
            button.pack(side=tk.LEFT, padx=5, pady=5)

        self.duan_confirm_button.pack(pady=10)

    def toggle_duan_card(self, card):
        """切换断张选择"""
        if card in self.duan_selected:
            self.duan_selected.remove(card)
        else:
            self.duan_selected.add(card)

    def check_duan_answer(self):
        """检查断张答案"""
        correct_duan_cards = set(self.duan_cards)
        user_selected = self.duan_selected

        self.total_questions += 1
        if user_selected == correct_duan_cards:
            self.total_score += 10
            self.correct_count += 1
            if len(correct_duan_cards) == 0:
                self.answer_label.config(text="回答正确！没有断张 (+10分)", fg="green")
            else:
                self.answer_label.config(
                    text=f"回答正确！断张为：{' '.join(sorted(correct_duan_cards, key=lambda x: CARD_ORDER[x]))} (+10分)",
                    fg="green")
        else:
            missing = correct_duan_cards - user_selected
            extra = user_selected - correct_duan_cards

            error_msg = "回答错误！"
            if missing:
                error_msg += f"漏选了：{' '.join(sorted(missing, key=lambda x: CARD_ORDER[x]))}"
            if extra:
                if missing:
                    error_msg += "；"
                error_msg += f"多选了：{' '.join(sorted(extra, key=lambda x: CARD_ORDER[x]))}"

            if correct_duan_cards:
                error_msg += f"；正确答案是：{' '.join(sorted(correct_duan_cards, key=lambda x: CARD_ORDER[x]))}"
            else:
                error_msg += "；正确答案是：没有断张"

            self.answer_label.config(text=error_msg, fg="red")

        self.duan_confirm_button.pack_forget()
        self.next_question_button.pack(pady=10)

    def show_count_question(self):
        """显示数量测验"""
        if self.current_count_question < len(self.count_questions_order):
            self.duan_frame.pack_forget()
            self.next_question_button.pack_forget()
            self.answer_label.config(text="")
            self.count_frame.pack()

            # 清除之前的选项
            for widget in self.count_options_frame.winfo_children():
                widget.destroy()

            card = self.count_questions_order[self.current_count_question]
            self.current_card_label.config(text=f"{card}")

            correct_count = self.remaining_card_count.get(card, 0)
            options = ['0', '1', '2', '3', '4']

            for option in options:
                button = tk.Button(
                    self.count_options_frame,
                    text=option,
                    command=lambda opt=option: self.check_count_answer(opt, correct_count),
                    font=("Microsoft YaHei", 12),
                    width=3,
                    height=1,
                    cursor="hand2"
                )
                button.pack(side=tk.LEFT, padx=5, pady=5)
        else:
            self.finish_quiz()

    def check_count_answer(self, answer, correct_count):
        """检查数量答案"""
        self.total_questions += 1
        if answer == str(correct_count):
            self.total_score += 6
            self.correct_count += 1
            self.answer_label.config(text="回答正确！ (+6分)", fg="green")
        else:
            self.answer_label.config(text=f"回答错误！正确答案是：{correct_count}", fg="red")

        self.next_question_button.pack(pady=10)

    def next_question(self):
        """进入下一题"""
        if self.game_phase == "quiz_duan":
            self.game_phase = "quiz_count"
            self.current_count_question = 0
            self.show_count_question()
        elif self.game_phase == "quiz_count":
            self.current_count_question += 1
            self.show_count_question()

    def finish_quiz(self):
        """完成测验"""
        self.quiz_frame.place_forget()

        accuracy = (self.correct_count / self.total_questions * 100) if self.total_questions > 0 else 0

        result_text = f"所有训练完成！\n"
        result_text += f"总分：{self.total_score}分 / 100分\n"
        result_text += f"正确率：{accuracy:.1f}%\n"
        result_text += f"答对：{self.correct_count}题 / 总题数：{self.total_questions}题"

        self.progress_label.config(text=result_text)
        messagebox.showinfo("完成", result_text)

    def run(self):
        """运行程序"""
        self.root.mainloop()


# 主程序
if __name__ == "__main__":
    app = MemoryGameApp()
    app.run()