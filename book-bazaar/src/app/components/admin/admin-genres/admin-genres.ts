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
import { Genre } from '../../../model/genre';
import { GenreService } from '../../../services/genre/genre-service';
import { SimpleEntityFormDialog, SimpleEntityDialogData } from '../simple-entity-form-dialog/simple-entity-form-dialog';
import { ConfirmDialog } from '../../dialog/confirm-dialog';

@Component({
  selector: 'app-admin-genres',
  standalone: true,
  imports: [
    MatTableModule, MatPaginatorModule, MatButtonModule, MatIconModule,
    MatInputModule, MatFormFieldModule, MatTooltipModule, MatDialogModule,
    MatProgressSpinnerModule, FormsModule,
  ],
  templateUrl: './admin-genres.html',
})
export class AdminGenresPage implements OnInit {
  private genreService = inject(GenreService);
  private dialog = inject(MatDialog);

  genres = signal<Genre[]>([]);
  total = signal(0);
  loading = signal(true);

  pageIndex = 0;
  pageSize = 10;
  searchQuery = '';

  readonly columns = ['name', 'description', 'actions'];

  private search$ = new Subject<string>();

  constructor() {
    this.search$.pipe(
      debounceTime(400), distinctUntilChanged(),
      switchMap(q => { this.pageIndex = 0; this.loading.set(true); return this.genreService.getGenres(0, this.pageSize, q || undefined); }),
      takeUntilDestroyed(),
    ).subscribe(page => { this.genres.set(page.items); this.total.set(Number(page.total)); this.loading.set(false); });
  }

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.genreService.getGenres(this.pageIndex, this.pageSize, this.searchQuery || undefined).subscribe({
      next: page => { this.genres.set(page.items); this.total.set(Number(page.total)); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  onSearch(v: string): void { this.search$.next(v); }
  onPage(e: PageEvent): void { this.pageIndex = e.pageIndex; this.pageSize = e.pageSize; this.load(); }

  private dialogData(g?: Genre): SimpleEntityDialogData {
    return {
      title: g ? 'Edit Genre' : 'Create Genre',
      fields: [
        { key: 'name', label: 'Name', maxLength: 50 },
        { key: 'description', label: 'Description', maxLength: 255, multiline: true },
      ],
      initialValues: g ? { name: g.name, description: g.description } : undefined,
    };
  }

  openCreate(): void {
    this.dialog.open(SimpleEntityFormDialog, { data: this.dialogData(), disableClose: true })
      .afterClosed().subscribe(v => { if (v) this.genreService.createGenre(v).subscribe(() => this.load()); });
  }

  openEdit(g: Genre): void {
    this.dialog.open(SimpleEntityFormDialog, { data: this.dialogData(g), disableClose: true })
      .afterClosed().subscribe(v => { if (v) this.genreService.updateGenre(g.id!, v).subscribe(() => this.load()); });
  }

  openDelete(g: Genre): void {
    this.dialog.open(ConfirmDialog, { data: { title: 'Delete Genre?', message: 'This action cannot be undone. Are you sure you want to remove this genre permanently?' } })
      .afterClosed().subscribe(ok => { if (ok) this.genreService.deleteGenre(g.id!).subscribe(() => this.load()); });
  }
}
