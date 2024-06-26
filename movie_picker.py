import csv
import random
import tkinter as tk
import webbrowser
from dataclasses import dataclass
from tkinter import ttk


@dataclass
class Movie:
    watched: bool
    original_title: str
    imdb_rating: float
    runtime: float
    year: int
    genres: list
    url: str


def read_csv(filename):
    movies = []
    genres_set = set()
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            genres = row['Genres'].split(', ')
            movie = Movie(
                watched=row['Watched'] == 'True',
                original_title=row['Title'],
                imdb_rating=float(row['IMDb Rating']),
                runtime=int(row['Runtime (mins)']),
                year=int(row['Year']),
                genres=genres,
                url=row['URL']
            )
            movies.append(movie)
            genres_set.update(genres)
    return movies, sorted(genres_set)

movies, genres = read_csv('movie_list.csv')


class MovieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Pick App")
        
        self.movies, self.genres = read_csv('movie_list.csv')
        random.shuffle(self.movies)

        self.selected_genres = set()
        self.selected_rating = None

        self.create_widgets()
        self.display_movies()

    def create_widgets(self):
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.first_frame = ttk.Frame(self.top_frame)
        self.first_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(self.first_frame, text="Search: ").pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(self.first_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda event: self.display_movies())

        # Clear button for search entry
        self.clear_button = ttk.Button(self.first_frame, text="Clear", command=self.clear_search)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Remove Filters button
        self.remove_filters_button = ttk.Button(self.first_frame, text="Remove Filters", width=18, command=self.remove_filters)
        self.remove_filters_button.pack(side=tk.LEFT, padx=5)

        # Random movie selection button
        self.random_button = ttk.Button(self.first_frame, text="Random Movie", width=18, command=self.display_random_movie)
        self.random_button.pack(side=tk.LEFT, padx=5)

        self.second_frame = ttk.Frame(self.top_frame)
        self.second_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Watched filter
        self.watched_filter = ttk.Combobox(self.second_frame,\
                                            values=[" All", " Watched", " Unwatched"],\
                                            width=10,\
                                            style="TMenubutton",\
                                            state="readonly")
        self.watched_filter.set(self.watched_filter["values"][0])
        self.watched_filter.bind("<<ComboboxSelected>>", lambda e: (self.display_movies(),self.watched_filter.select_clear()))
        self.watched_filter.pack(side=tk.LEFT, padx=10)

        # Genre filter
        self.genre_menu = ttk.Menubutton(self.second_frame, text="Genres")
        self.genre_menu.pack(side=tk.LEFT, padx=10)

        self.genre_menu.menu = tk.Menu(self.genre_menu, tearoff=0)
        self.genre_menu["menu"] = self.genre_menu.menu

        for genre in self.genres:
            self.genre_menu.menu.add_command(label=genre, command=lambda g=genre: self.add_genre(g))

        self.active_filters_frame = ttk.Frame(self.top_frame)
        self.active_filters_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # IMDb rating filter
        self.rating_menu = ttk.Menubutton(self.second_frame, text="IMDb Rating")
        self.rating_menu.pack(side=tk.LEFT, padx=10)

        self.rating_menu.menu = tk.Menu(self.rating_menu, tearoff=0)
        self.rating_menu["menu"] = self.rating_menu.menu

        rating_values = ['6+', '6.5+', '7+', '7.5+', '8+', '8.5+', '9+']
        for rating in rating_values:
            self.rating_menu.menu.add_command(label=rating, command=lambda r=rating: self.add_rating(r))

        # Year filter
        ttk.Label(self.second_frame, text="Year:").pack(side=tk.LEFT, padx=5)

        self.year_from_entry = ttk.Entry(self.second_frame, width=5)
        self.year_from_entry.pack(side=tk.LEFT, padx=5)
        self.year_from_entry.bind("<KeyRelease>", lambda event: self.display_movies())

        ttk.Label(self.second_frame, text="to").pack(side=tk.LEFT)

        self.year_to_entry = ttk.Entry(self.second_frame, width=5)
        self.year_to_entry.pack(side=tk.LEFT, padx=5)
        self.year_to_entry.bind("<KeyRelease>", lambda event: self.display_movies())

        # Runtime filter
        ttk.Label(self.second_frame, text="Max Runtime (mins):").pack(side=tk.LEFT, padx=5)
        self.runtime_label = ttk.Label(self.second_frame, text="240", width=3)
        self.runtime_label.pack(side=tk.LEFT)

        self.runtime_slider = ttk.Scale(self.second_frame, from_=3, to_=8, orient=tk.HORIZONTAL)
        self.runtime_slider.set(8)
        self.runtime_slider.bind("<ButtonRelease-1>", lambda e: (self.runtime_slider.set(int(self.runtime_slider.get())),
                                                                 self.runtime_label.config(text=int(self.runtime_slider.get()*30)),
                                                                 self.display_movies()))
        self.runtime_slider.pack(side=tk.LEFT, padx=3)

        # Movie list frame
        self.movie_frame = ttk.Frame(self.root)
        self.movie_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Movie list
        columns = ('Title', 'Year', 'Rating', 'Runtime', 'Genres')
        self.movie_tree = ttk.Treeview(self.movie_frame, columns=columns, show='headings')
        
        for col in columns:
            self.movie_tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
        
        self.movie_tree.config(selectmode='browse') # Disable multiple selection
        self.movie_tree.column('Title', width=200)
        self.movie_tree.column('Year', width=50, anchor=tk.CENTER)
        self.movie_tree.column('Rating', width=50, anchor=tk.CENTER)
        self.movie_tree.column('Runtime', width=50, anchor=tk.CENTER)
        self.movie_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.movie_tree.bind("<Double-1>", self.open_movie_url)
        self.movie_tree.bind("<Button-3>", lambda e: self.change_watched_status(e))

        # Movie list scrollbar
        self.scrollbar = ttk.Scrollbar(self.movie_frame, orient=tk.VERTICAL, command=self.movie_tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.movie_tree.configure(yscrollcommand=self.scrollbar.set)

        self.sub_label = ttk.Label(self.root)
        self.sub_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

    def add_genre(self, genre):
        if genre not in self.selected_genres:
            self.selected_genres.add(genre)
            btn = ttk.Button(self.active_filters_frame, text=f"{genre} ❌", width=len(genre) + 5)
            btn.config(command=lambda: self.remove_genre(genre, btn))
            btn.pack(side=tk.LEFT, padx=5)

            self.update_active_filters_frame()
            self.display_movies()

    def remove_genre(self, genre, button):
        self.selected_genres.remove(genre)
        button.destroy()
        self.update_active_filters_frame()
        self.display_movies()

    def add_rating(self, rating):
        if self.selected_rating:
            self.remove_rating(self.selected_rating, self.rating_button)

        self.selected_rating = rating
        self.rating_button = ttk.Button(self.active_filters_frame, text=f"IMDb Rating {rating} ❌", width=len(rating) + 15)
        self.rating_button.config(command=lambda: self.remove_rating(rating, self.rating_button))
        self.rating_button.pack(side=tk.LEFT, padx=5)

        self.update_active_filters_frame()
        self.display_movies()

    def remove_rating(self, rating, button):
        self.selected_rating = None
        button.destroy()
        self.update_active_filters_frame()
        self.display_movies()
        
        
    def display_movies(self):
        self.movie_tree.delete(*self.movie_tree.get_children())

        rating_filter = float(self.selected_rating.replace('+', '')) if self.selected_rating else 0
        year_from_filter = int(self.year_from_entry.get() or 0)
        year_to_filter = int(self.year_to_entry.get() or 9999)
        runtime_filter = int(self.runtime_label['text'])

        search_text = self.search_entry.get().strip().lower()

        movie_count = 0
        watched_count = 0
        for movie in self.movies:
            if search_text and search_text not in movie.original_title.lower():
                continue

            if movie.imdb_rating < rating_filter:
                continue

            if movie.year < year_from_filter or movie.year > year_to_filter:
                continue

            if movie.runtime > runtime_filter:
                continue

            if not self.selected_genres.issubset(movie.genres):
                continue
            
            watch_filter = self.watched_filter.get().lstrip()
            if (watch_filter == "Watched" and not movie.watched) or\
                (watch_filter == "Unwatched" and movie.watched):
                continue

            movie_count += 1
            if movie.watched:
                watched_count += 1

            item_tags = ('watched' if movie.watched else 'unwatched',)
            self.movie_tree.insert('', tk.END, values=(movie.original_title, movie.year, movie.imdb_rating, movie.runtime, ', '.join(movie.genres), movie.url), tags=item_tags)
        
        self.movie_tree.tag_configure('watched', background='#C7F7C7')
        self.movie_tree.tag_configure('unwatched', background='#FFBFA8')
        
        string = f"Total movies: {movie_count} | Watched {watched_count} : %{watched_count/movie_count*100:.2f} | Unwatched {movie_count-watched_count} : %{(movie_count-watched_count)/movie_count*100:.2f} | Total genres: {len(self.genres)} |\tDouble click to a movie to open IMDb page"
        self.sub_label.config(text=string)

    def remove_filters(self):
        self.search_entry.delete(0, tk.END)
        self.watched_filter.set(" All")
        self.selected_genres.clear()
        self.selected_rating = None
        self.year_from_entry.delete(0, tk.END)
        self.year_to_entry.delete(0, tk.END)
        self.runtime_slider.set(8)
        self.runtime_label.config(text="240")
        for widget in self.active_filters_frame.winfo_children():
            widget.destroy()
        self.update_active_filters_frame()        
        self.display_movies()
    
    # gets a random movie from treeview which is the displayed list
    # creates a new window displaying the movie with all its details
    def display_random_movie(self):
        selected_movie = random.choice(self.movie_tree.get_children())
        is_watched = self.movie_tree.item(selected_movie)['tags'][0] == 'watched'
        for movie in self.movies:
            if movie.original_title == self.movie_tree.item(selected_movie)['values'][0]:
                selected_movie = movie
                break
            
        new_window = tk.Toplevel(self.root)
        new_window.title("Random Movie")
        new_window.minsize(300, 200)
        ttk.Label(new_window, text=selected_movie.original_title, font=("Times New Roman Bold", 20)).pack(pady=5)
        ttk.Label(new_window, text=f"Year: {selected_movie.year}", font=("Times New Roman", 13)).pack(pady=5)
        ttk.Label(new_window, text=f"IMDb Rating: {selected_movie.imdb_rating}", font=("Times New Roman", 12)).pack(pady=5)
        ttk.Label(new_window, text=f"Duration: {selected_movie.runtime:.0f} mins", font=("Times New Roman", 12)).pack(pady=5)
        ttk.Label(new_window, text=f"Genres: {', '.join(selected_movie.genres)}", font=("Times New Roman", 10)).pack(pady=5)
        ttk.Button(new_window, text="Open IMDb Page", command=lambda: webbrowser.open(selected_movie.url)).pack(pady=5)
        ttk.Label(new_window, text="").pack()
        if is_watched:
            ttk.Label(new_window, text="You have already watched this movie!", font=("Times New Roman", 12), foreground="red").pack(pady=5)
        else:
            ttk.Label(new_window, text="You haven't watched this movie yet!", font=("Times New Roman", 12), foreground="green").pack(pady=5)

    def update_active_filters_frame(self):
        if self.selected_genres or self.selected_rating:
            self.active_filters_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        else:
            self.active_filters_frame.pack_forget()  # Hide the frame if no filters are active
 
    def open_movie_url(self, event):
        selected_item = self.movie_tree.focus()
        if not selected_item:
            return  # No item selected

        url = self.movie_tree.item(selected_item)['values'][-1]

        if url:
            webbrowser.open(url)
            
    def sort_column(self, col, reverse):
        items = [(self.movie_tree.set(item, col), item) for item in self.movie_tree.get_children('')]
        items.sort(reverse=reverse)

        for index, (val, item) in enumerate(items):
            self.movie_tree.move(item, '', index)

        # Reverse sort direction for next time
        self.movie_tree.heading(col, command=lambda: self.sort_column(col, not reverse))
        
    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.display_movies()
    
    # changes the watched status of the selected movie
    def change_watched_status(self, event):
        selected_item = self.movie_tree.focus()
        if not selected_item:
            return
        
        for movie in self.movies:
            if movie.original_title == self.movie_tree.item(selected_item)['values'][0]:
                movie.watched = not movie.watched
                break
        self.display_movies()
        
        

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieApp(root)
    root.mainloop()