import { Component, inject, OnInit, signal } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { debounceTime, distinctUntilChanged, Subject, switchMap } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Author } from '../../../model/author';
import { AuthorService } from '../../../services/author/author-service';
import { SimpleEntityFormDialog, SimpleEntityDialogData } from '../simple-entity-form-dialog/simple-entity-form-dialog';
import { ConfirmDialog } from '../../dialog/confirm-dialog';

@Component({
  selector: 'app-admin-authors',
  standalone: true,
  imports: [
    MatTableModule, MatPaginatorModule, MatButtonModule, MatIconModule,
    MatInputModule, MatFormFieldModule, MatTooltipModule, MatDialogModule,
    MatProgressSpinnerModule, FormsModule,
  ],
  templateUrl: './admin-authors.html',
})
export class AdminAuthorsPage implements OnInit {
  private authorService = inject(AuthorService);
  private dialog = inject(MatDialog);

  authors = signal<Author[]>([]);
  total = signal(0);
  loading = signal(true);

  pageIndex = 0;
  pageSize = 10;
  searchQuery = '';

  readonly columns = ['name', 'bio', 'actions'];

  private search$ = new Subject<string>();

  constructor() {
    this.search$.pipe(
      debounceTime(400),
      distinctUntilChanged(),
      switchMap(q => {
        this.pageIndex = 0;
        this.loading.set(true);
        return this.authorService.getAuthors(0, this.pageSize, q || undefined);
      }),
      takeUntilDestroyed(),
    ).subscribe(page => {
      this.authors.set(page.items);
      this.total.set(Number(page.total));
      this.loading.set(false);
    });
  }

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.authorService.getAuthors(this.pageIndex, this.pageSize, this.searchQuery || undefined).subscribe({
      next: page => { this.authors.set(page.items); this.total.set(Number(page.total)); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  onSearch(value: string): void { this.search$.next(value); }
  onPage(event: PageEvent): void { this.pageIndex = event.pageIndex; this.pageSize = event.pageSize; this.load(); }

  private dialogData(author?: Author): SimpleEntityDialogData {
    return {
      title: author ? 'Edit Author' : 'Create Author',
      fields: [
        { key: 'name', label: 'Name', maxLength: 100 },
        { key: 'bio', label: 'Bio', maxLength: 500, multiline: true, required: false },
      ],
      initialValues: author ? { name: author.name, bio: author.bio } : undefined,
    };
  }

  openCreate(): void {
    this.dialog.open(SimpleEntityFormDialog, { data: this.dialogData(), disableClose: true })
      .afterClosed().subscribe(v => { if (v) this.authorService.createAuthor(v).subscribe(() => this.load()); });
  }

  openEdit(author: Author): void {
    this.dialog.open(SimpleEntityFormDialog, { data: this.dialogData(author), disableClose: true })
      .afterClosed().subscribe(v => { if (v) this.authorService.updateAuthor(author.id!, v).subscribe(() => this.load()); });
  }

  openDelete(author: Author): void {
    this.dialog.open(ConfirmDialog, { data: { title: 'Delete Author?', message: 'This action cannot be undone. Are you sure you want to remove this author permanently?' } })
      .afterClosed().subscribe(ok => { if (ok) this.authorService.deleteAuthor(author.id!).subscribe(() => this.load()); });
  }
}
