"""Crossword Puzzle.

http://www.gamedesign.jp/flash/crossword/crossword_jp.html
"""

import random
import time
import tkinter as tk
import tkinter.messagebox
from collections import Counter
from pathlib import Path

import pygame as pg
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN, QUIT


class Crossword:
    """Crossword Puzzle"""

    DATA_DIR = Path(__file__).parent / "crosswordpy_data"
    ALPHABET_NUM = 26

    def __init__(self) -> None:
        """初期化"""
        tk.Tk().wm_withdraw()
        self.wd = 52
        self.wds = self.wd * 11
        self.probs = []  # 全問題
        for file in self.DATA_DIR.glob("*.txt"):
            self.probs.append(file.read_text())

    def draw(self) -> None:
        """描画"""
        sc, wd, wds = self.screen, self.wd, self.wds
        bk, wh, bl = (0, 0, 0), (255, 255, 255), (0, 0, 128)
        sc.fill((240, 240, 240))
        level = ["Beginner", "Easy", "Normal", "Hard", "Expert"][self.pos]
        t = self.font_small.render(level, True, bl)  # noqa: FBT003
        sc.blit(t, (wds + 22, 16))
        for i in range(12):
            pg.draw.line(sc, bk, (0, wd * i), (wds, wd * i))
            pg.draw.line(sc, bk, (wd * i, 0), (wd * i, wds))
        for y in range(11):
            for x in range(11):
                c, h, p = (
                    self.ans[x + y * 11],
                    self.hint[x + y * 11],
                    self.prob[x + y * 11],
                )
                pg.draw.rect(
                    sc,
                    bk if p == " " else (255, 165, 0) if self.cur == p else wh,
                    (x * wd + 1, y * wd + 1, wd - 1, wd - 1),
                )
                if c != " ":
                    t = self.font.render(c, True, bl if h != " " else (64, 64, 64))  # noqa: FBT003
                    sc.blit(t, (x * wd - t.get_width() // 2 + 27, y * wd + 9))
        for i in range(self.ALPHABET_NUM + 1):
            if i == self.ALPHABET_NUM or not self.done[i]:
                pg.draw.rect(
                    sc,
                    (255, 255, 255),
                    ((i % 3) * wd + wds + 14, (i // 3) * wd + 46, 50, 50),
                )
            pg.draw.rect(
                sc,
                (108, 108, 108),
                ((i % 3) * wd + wds + 14, (i // 3) * wd + 46, 50, 50),
                1,
            )
            if i < self.ALPHABET_NUM:
                t = self.font.render(chr(i + 65), True, (168, 168, 168) if self.done[i] else (64, 64, 64))  # noqa: FBT003
                sc.blit(
                    t,
                    ((i % 3) * wd - t.get_width() // 2 + wds + 38, (i // 3) * wd + 52),
                )
        if self.ok:
            pg.draw.rect(sc, (255, 248, 208), (wds + 20, 9 * wd + 50, 140, 48))
            pg.draw.rect(sc, (0, 0, 0), (wds + 20, 9 * wd + 50, 140, 48), 1)
            t = self.font.render("NEXT", True, bl)  # noqa: FBT003
            sc.blit(t, (wds + 30, 9 * wd + 56))

    def set_prob(self) -> None:
        """問題設定"""
        self.pos += 1  # ステージ番号(0 ~ 4)
        self.ok = False  # ステージが完成かどうか
        self.cur = ""  # 選択中の文字
        s = random.choice(self.probs).rstrip("\n")
        if random.random() < 0.5:
            s = "\n".join("".join(c) for c in zip(*s.split("\n"), strict=False))
        self.prob = s.replace("\n", "")
        n = (5 - self.pos) * 2 + random.randint(0, 2)
        t = list(Counter(self.prob.replace(" ", "")).items())
        random.shuffle(t)
        r = sorted(t, key=lambda x: x[1])  # noqa: FURB118
        e = set(["" if i < v - 1 else k for k, v in r for i in range(v)][:n]) - {""}
        self.hint = "".join(c if c in e else " " for c in self.prob)
        self.ans = list(self.hint)
        self.reset_done()

    def reset_done(self) -> None:
        """「済み」をリセット"""
        self.done = [True] * self.ALPHABET_NUM  # 全て指定済み
        for c in set(self.prob) - set(self.ans):
            self.done[ord(c) - 65] = False

    def put(self, c: str) -> None:
        """置く"""
        if not self.cur or (c != " " and self.done[ord(c) - 65]):
            return
        for i in range(11 * 11):
            if self.cur == self.prob[i]:
                self.ans[i] = c
        self.reset_done()
        self.ok = "".join(self.ans) == self.prob

    def run(self) -> None:  # noqa: C901, PLR0912
        """ゲーム実行"""
        pg.init()
        pg.display.set_caption("Crossword Puzzle")
        pg.display.set_mode((752, self.wds + 1), 0, 32)
        self.screen = pg.display.get_surface()
        self.font = pg.font.Font(None, 64)
        self.font_small = pg.font.Font(None, 32)
        while True:  # noqa: PLR1702
            total_time = 0.0
            self.pos = -1
            for _ in range(5):
                tm = time.time()
                self.set_prob()
                complete = False  # ステージクリアかどうか
                chk = False  # total_timeに加算したかどうか
                while not complete:
                    for ev in pg.event.get():
                        if ev.type == QUIT:
                            pg.quit()
                            return
                        if ev.type == KEYDOWN:
                            if not self.ok:
                                if ev.key == 32 or 65 <= ev.key <= 90:
                                    self.put(chr(ev.key))
                                elif 97 <= ev.key <= 122:
                                    self.put(chr(ev.key - 97 + 65))
                        elif ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                            x, y = ev.pos
                            i1, j1 = x // self.wd, y // self.wd
                            i2, j2 = (x - self.wds - 14) // self.wd, (y - 46) // self.wd
                            i3, j3 = (
                                (x - self.wds - 20) // 140,
                                (y - 9 * self.wd - 50) // 48,
                            )
                            if self.ok:
                                if i3 == 0 and j3 == 0:
                                    complete = True
                            elif (
                                0 <= i1 < 11
                                and 0 <= j1 < 11
                                and self.hint[i1 + j1 * 11] == " "
                                and self.prob[i1 + j1 * 11] != " "
                            ):
                                self.cur = self.prob[i1 + j1 * 11]
                            elif 0 <= i2 < 3 and 0 <= j2 < 9:
                                self.put(" " if (i2, j2) == (2, 8) else chr(i2 + j2 * 3 + 65))
                    self.draw()
                    pg.display.update()
                    pg.time.wait(50)
                    if self.ok and not chk:
                        chk = True
                        total_time += time.time() - tm
                        if self.pos == 4:
                            tkinter.messagebox.showinfo(
                                "Crossword Puzzle",
                                f"Congratulations ({total_time:.1f} sec)",
                            )
