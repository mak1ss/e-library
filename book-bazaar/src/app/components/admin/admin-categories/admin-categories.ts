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
import { Category } from '../../../model/category';
import { CategoryService } from '../../../services/category/category-service';
import { SimpleEntityFormDialog, SimpleEntityDialogData } from '../simple-entity-form-dialog/simple-entity-form-dialog';
import { ConfirmDialog } from '../../dialog/confirm-dialog';

@Component({
  selector: 'app-admin-categories',
  standalone: true,
  imports: [
    MatTableModule, MatPaginatorModule, MatButtonModule, MatIconModule,
    MatInputModule, MatFormFieldModule, MatTooltipModule, MatDialogModule,
    MatProgressSpinnerModule, FormsModule,
  ],
  templateUrl: './admin-categories.html',
})
export class AdminCategoriesPage implements OnInit {
  private categoryService = inject(CategoryService);
  private dialog = inject(MatDialog);

  categories = signal<Category[]>([]);
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
      switchMap(q => { this.pageIndex = 0; this.loading.set(true); return this.categoryService.getCategories(0, this.pageSize, q || undefined); }),
      takeUntilDestroyed(),
    ).subscribe(page => { this.categories.set(page.items); this.total.set(Number(page.total)); this.loading.set(false); });
  }

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.categoryService.getCategories(this.pageIndex, this.pageSize, this.searchQuery || undefined).subscribe({
      next: page => { this.categories.set(page.items); this.total.set(Number(page.total)); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  onSearch(v: string): void { this.search$.next(v); }
  onPage(e: PageEvent): void { this.pageIndex = e.pageIndex; this.pageSize = e.pageSize; this.load(); }

  private dialogData(c?: Category): SimpleEntityDialogData {
    return {
      title: c ? 'Edit Category' : 'Create Category',
      fields: [
        { key: 'name', label: 'Name', maxLength: 100 },
        { key: 'description', label: 'Description', maxLength: 255, multiline: true },
      ],
      initialValues: c ? { name: c.name, description: c.description } : undefined,
    };
  }

  openCreate(): void {
    this.dialog.open(SimpleEntityFormDialog, { data: this.dialogData(), disableClose: true })
      .afterClosed().subscribe(v => { if (v) this.categoryService.createCategory(v).subscribe(() => this.load()); });
  }

  openEdit(c: Category): void {
    this.dialog.open(SimpleEntityFormDialog, { data: this.dialogData(c), disableClose: true })
      .afterClosed().subscribe(v => { if (v) this.categoryService.updateCategory(c.id!, v).subscribe(() => this.load()); });
  }

  openDelete(c: Category): void {
    this.dialog.open(ConfirmDialog, { data: { title: 'Delete Category?', message: 'This action cannot be undone. Are you sure you want to remove this category permanently?' } })
      .afterClosed().subscribe(ok => { if (ok) this.categoryService.deleteCategory(c.id!).subscribe(() => this.load()); });
  }
}
