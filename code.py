import tkinter as tk
from tkinter import messagebox


class DartsGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("101 Darts Scorekeeper")

        # --- Game state ---
        self.player_names = ["Player 1", "Player 2"]
        self.scores = [101, 101]
        self.current_player = 0  # 0 = P1, 1 = P2
        self.start_turn_score = 101
        self.turn_total = 0
        self.dart_num = 1
        self.winner = None
        self.darts_per_turn = 6  

        # --- UI variables ---
        self.p1_name_var = tk.StringVar()
        self.p2_name_var = tk.StringVar()
        self.throw_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self._build_setup_screen()

    # ---------------- UI BUILD ----------------
    def _clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _build_setup_screen(self):
        self._clear_root()

        tk.Label(self.root, text="Enter player names").grid(row=0, column=0, columnspan=2, pady=(10, 5))

        tk.Label(self.root, text="Player 1:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable = self.p1_name_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Player 2:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.p2_name_var).grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Start Game", command=self.start_game).grid(row=3, column=0, columnspan=2, pady=10)

    def _build_game_screen(self):
        self._clear_root()

        # Scoreboard
        self.p1_score_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.p2_score_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.p1_score_label.grid(row=0, column=0, padx=15, pady=10)
        self.p2_score_label.grid(row=0, column=1, padx=15, pady=10)

        # Status
        tk.Label(self.root, textvariable=self.status_var, wraplength=380, justify="left").grid(
            row=1, column=0, columnspan=2, padx=15, pady=10, sticky="w"
        )

        # Throw input
        tk.Label(self.root, text="Throw score:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.throw_entry = tk.Entry(self.root, textvariable=self.throw_var)
        self.throw_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        tk.Button(self.root, text="Submit Throw", command=self.submit_throw).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(self.root, text="New Game", command=self.reset_to_setup).grid(row=3, column=1, padx=10, pady=10)

        # Log box (optional but helpful)
        self.log = tk.Text(self.root, height=10, width=52, state="disabled")
        self.log.grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 15))

        self._refresh_ui()
        self.throw_entry.focus_set()

    # ---------------- GAME CONTROL ----------------
    def start_game(self):
        p1 = self.p1_name_var.get().strip() or "Player 1"
        p2 = self.p2_name_var.get().strip() or "Player 2"
        self.player_names = [p1, p2]

        self.scores = [101, 101]
        self.current_player = 0
        self.start_turn_score = self.scores[self.current_player]
        self.turn_total = 0
        self.dart_num = 1
        self.winner = None

        self._build_game_screen()
        self._log(f"Game started: {p1} vs {p2}\n")

    def reset_to_setup(self):
        self._build_setup_screen()

    def submit_throw(self):
        if self.winner is not None:
            return

        raw = self.throw_var.get().strip()
        if not raw:
            messagebox.showwarning("Invalid input", "Enter a throw score.")
            return

        # Validate int and range (0..60 typical)
        try:
            throw = int(raw)
        except ValueError:
            messagebox.showwarning("Invalid input", "Throw must be a whole number.")
            return

        if throw < 0 or throw > 60:
            messagebox.showwarning("Invalid input", "Throw must be between 0 and 60.")
            return

        p = self.current_player
        name = self.player_names[p]

        # Apply throw to turn total, compute temp score (like your console code)
        self.turn_total += throw
        temp_score = self.start_turn_score - self.turn_total

        self._log(f"{name} dart {self.dart_num}: {throw} -> remaining {temp_score}\n")

        # Bust / Win / Continue
        if temp_score < 0:
            # Bust: revert to start of round, end turn immediately
            self._log("BUST! Score reverts to start of turn.\n\n")
            self._end_turn(bust=True)
            return

        if temp_score == 0:
            self.scores[p] = 0
            self.winner = name
            self._refresh_ui()
            self._log(f"{name} WINS!\n")
            messagebox.showinfo("Winner", f"The winner is {name}!")
            return

        # Not bust, not win: continue if darts remain
        if self.dart_num >= self.darts_per_turn:
            # commit end-of-turn score
            self.scores[p] = temp_score
            self._log(f"End of turn. {name} now needs {self.scores[p]}.\n\n")
            self._end_turn(bust=False)
        else:
            self.dart_num += 1
            self._refresh_ui()

        self.throw_var.set("")
        self.throw_entry.focus_set()

    def _end_turn(self, bust: bool):
        # If bust: score stays at start_turn_score (already true), no commit
        # If not bust: score was committed before calling this
        self.current_player = 1 - self.current_player
        self.start_turn_score = self.scores[self.current_player]
        self.turn_total = 0
        self.dart_num = 1
        self._refresh_ui()

    # ---------------- UI HELPERS ----------------
    def _refresh_ui(self):
        p1, p2 = self.player_names
        s1, s2 = self.scores

        self.p1_score_label.config(text=f"{p1}: {s1}")
        self.p2_score_label.config(text=f"{p2}: {s2}")

        cur_name = self.player_names[self.current_player]
        self.status_var.set(
            f"Turn: {cur_name}\n"
            f"Dart: {self.dart_num}/{self.darts_per_turn}\n"
            f"Starting score this turn: {self.start_turn_score}\n"
            f"Turn total so far: {self.turn_total}"
        )

    def _log(self, msg: str):
        self.log.config(state="normal")
        self.log.insert("end", msg)
        self.log.see("end")
        self.log.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = DartsGameGUI(root)
    root.mainloop()
