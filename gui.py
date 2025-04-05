import customtkinter as ctk
import tkinter as tk
import main
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("760x740")
app.title("🎬 Movie Genre Mixer Chatbot")

# Chat Display using standard tk.Text
chat_display = tk.Text(
    app,
    width=88,
    height=25,
    bg="#FAF0E6",         # beige background
    fg="black",
    font=("Arial", 13),
    wrap="word",
    state="disabled"      # initially read-only
)
chat_display.pack(pady=10)

# Enable bot response styling
chat_display.tag_configure("bot_tag", foreground="#4169E1", font=("Arial", 13, "bold"))
chat_display.tag_configure("user_tag", foreground="black", font=("Arial", 13, "bold"))

def insert_chat_message(text, tag=None):
    chat_display.config(state="normal")
    chat_display.insert("end", text, tag)
    chat_display.see("end")
    chat_display.config(state="disabled")

insert_chat_message("👋 Welcome to Movie Genre Mixer!\nAsk me for movie suggestions based on your mood or genres like 'sci-fi romance'.\n\n")

# Entry Box
entry_frame = ctk.CTkFrame(app)
entry_frame.pack(pady=5)

entry = ctk.CTkEntry(entry_frame, placeholder_text="Type your message...", width=500)
entry.pack(side="left", padx=5)

def show_typing_animation():
    for _ in range(3):
        insert_chat_message(".")
        app.update()
        time.sleep(0.4)

def respond():
    user_input = entry.get()
    if not user_input.strip():
        return
    insert_chat_message(f"You: {user_input}\n")
    entry.delete(0, "end")
    insert_chat_message("🤖 Bot is typing")
    app.update()
    show_typing_animation()
    insert_chat_message("\n")

    response, _ = main.chatbot_response(user_input)
    insert_chat_message(f"🤖 Bot: {response}\n\n", "bot_tag")

def on_enter_key(event):
    respond()

entry.bind("<Return>", on_enter_key)

send_btn = ctk.CTkButton(entry_frame, text="Send", command=respond)
send_btn.pack(side="left", padx=10)

# Random Mix Button
def random_mix():
    insert_chat_message("🎲 Mixing random genres...\n")
    app.update()
    show_typing_animation()
    genres, movies = main.random_mix_movies()
    insert_chat_message(f"🎭 Genres Mixed: {', '.join(genres)}\n")
    response = main.format_movie_list(movies)
    insert_chat_message(f"{response}\n\n", "bot_tag")

random_btn = ctk.CTkButton(app, text="🎲 Random Mix", command=random_mix)
random_btn.pack(pady=5)

# Save to Watchlist
def save_watchlist():
    user_input = entry.get()
    if not user_input.strip():
        return
    msg = main.save_to_watchlist(user_input)
    insert_chat_message(f"{msg}\n\n")
    entry.delete(0, "end")

save_btn = ctk.CTkButton(app, text="⭐ Save to Watchlist", command=save_watchlist)
save_btn.pack(pady=5)

# Watchlist checkbox panel
watchlist_checkboxes = []
checkbox_frame = ctk.CTkFrame(app)
checkbox_frame.pack(pady=5)

def show_watchlist():
    for cb in watchlist_checkboxes:
        cb[0].destroy()
    watchlist_checkboxes.clear()

    insert_chat_message("📽️ Your Watchlist:\n")
    for title in main.get_watchlist():
        var = tk.BooleanVar()
        cb = ctk.CTkCheckBox(checkbox_frame, text=title, variable=var)
        cb.pack(anchor="w")
        watchlist_checkboxes.append((cb, var))
    insert_chat_message("\n")

watchlist_btn = ctk.CTkButton(app, text="📚 Show Watchlist", command=show_watchlist)
watchlist_btn.pack(pady=5)

def delete_selected():
    to_remove = [cb.cget("text") for cb, var in watchlist_checkboxes if var.get()]
    if to_remove:
        main.delete_from_watchlist(to_remove)
        insert_chat_message(f"🗑️ Removed: {', '.join(to_remove)}\n\n")
        show_watchlist()
    else:
        insert_chat_message("⚠️ No movies selected for deletion.\n\n")

delete_btn = ctk.CTkButton(app, text="❌ Delete Selected", command=delete_selected)
delete_btn.pack(pady=5)

app.mainloop()
