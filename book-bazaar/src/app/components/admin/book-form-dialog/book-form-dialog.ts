import { Component, inject, OnInit, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { forkJoin } from 'rxjs';
import { Book } from '../../../model/book';
import { Author } from '../../../model/author';
import { Category } from '../../../model/category';
import { Genre } from '../../../model/genre';
import { Publisher } from '../../../model/publisher';
import { AuthorService } from '../../../services/author/author-service';
import { CategoryService } from '../../../services/category/category-service';
import { GenreService } from '../../../services/genre/genre-service';
import { PublisherService } from '../../../services/publisher/publisher-service';
import { BookRequest } from '../../../services/book/book-service';

export interface BookFormDialogData {
  book?: Book;
}

export interface BookFormDialogResult {
  request: BookRequest;
  coverFile?: File;
}

@Component({
  selector: 'app-book-form-dialog',
  standalone: true,
  imports: [
    ReactiveFormsModule, MatDialogModule, MatButtonModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatSelectModule, MatDatepickerModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './book-form-dialog.html',
})
export class BookFormDialog implements OnInit {
  private fb = inject(FormBuilder);
  private authorService = inject(AuthorService);
  private categoryService = inject(CategoryService);
  private genreService = inject(GenreService);
  private publisherService = inject(PublisherService);

  readonly dialogRef = inject(MatDialogRef<BookFormDialog>);
  readonly data: BookFormDialogData = inject(MAT_DIALOG_DATA);

  authors = signal<Author[]>([]);
  categories = signal<Category[]>([]);
  genres = signal<Genre[]>([]);
  publishers = signal<Publisher[]>([]);
  loading = signal(true);

  coverFile = signal<File | null>(null);
  coverPreviewUrl = signal<string | null>(this.data.book?.imageUrl ?? null);

  readonly isEdit = !!this.data.book;

  form = this.fb.group({
    title: [this.data.book?.title ?? '', [Validators.required, Validators.maxLength(255)]],
    authorId: [this.data.book?.author?.id ?? null, Validators.required],
    categoryId: [this.data.book?.category?.id ?? null, Validators.required],
    publisherId: [this.data.book?.publisher?.id ?? null, Validators.required],
    genreIdList: [this.data.book?.bookGenres?.map(g => g.id) ?? [], Validators.required],
    description: [this.data.book?.description ?? '', Validators.maxLength(500)],
    ISBN: [this.data.book?.isbn ?? ''],
    releaseDate: [this.data.book?.releaseDate ? new Date(this.data.book.releaseDate) : null],
    price: [this.data.book?.price ?? null, [Validators.required, Validators.min(0)]],
  });

  ngOnInit(): void {
    forkJoin({
      authors: this.authorService.getAuthors(0, 200),
      categories: this.categoryService.getCategories(0, 100),
      genres: this.genreService.getGenres(0, 100),
      publishers: this.publisherService.getPublishers(0, 100),
    }).subscribe({
      next: ({ authors, categories, genres, publishers }) => {
        this.authors.set(authors.items);
        this.categories.set(categories.items);
        this.genres.set(genres.items);
        this.publishers.set(publishers.items);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    this.coverFile.set(file);
    this.coverPreviewUrl.set(URL.createObjectURL(file));
  }

  removeCover(): void {
    this.coverFile.set(null);
    this.coverPreviewUrl.set(null);
  }

  submit(): void {
    if (this.form.invalid) return;
    const v = this.form.value;
    const request: BookRequest = {
      title: v.title!,
      authorId: v.authorId!,
      categoryId: v.categoryId!,
      publisherId: v.publisherId!,
      genreIdList: (v.genreIdList ?? []) as number[],
      description: v.description ?? undefined,
      ISBN: v.ISBN ?? undefined,
      releaseDate: v.releaseDate ? (v.releaseDate as Date).toISOString().split('T')[0] : undefined,
      price: v.price!,
    };
    const result: BookFormDialogResult = {
      request,
      coverFile: this.coverFile() ?? undefined,
    };
    this.dialogRef.close(result);
  }
}
