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
import { Publisher } from '../../../model/publisher';
import { PublisherService } from '../../../services/publisher/publisher-service';
import { SimpleEntityFormDialog, SimpleEntityDialogData } from '../simple-entity-form-dialog/simple-entity-form-dialog';
import { ConfirmDialog } from '../../dialog/confirm-dialog';

@Component({
  selector: 'app-admin-publishers',
  standalone: true,
  imports: [
    MatTableModule, MatPaginatorModule, MatButtonModule, MatIconModule,
    MatInputModule, MatFormFieldModule, MatTooltipModule, MatDialogModule,
    MatProgressSpinnerModule, FormsModule,
  ],
  templateUrl: './admin-publishers.html',
})
export class AdminPublishersPage implements OnInit {
  private publisherService = inject(PublisherService);
  private dialog = inject(MatDialog);

  publishers = signal<Publisher[]>([]);
  total = signal(0);
  loading = signal(true);

  pageIndex = 0;
  pageSize = 10;
  searchQuery = '';

  readonly columns = ['name', 'address', 'actions'];

  private search$ = new Subject<string>();

  constructor() {
    this.search$.pipe(
      debounceTime(400), distinctUntilChanged(),
      switchMap(q => { this.pageIndex = 0; this.loading.set(true); return this.publisherService.getPublishers(0, this.pageSize, q || undefined); }),
      takeUntilDestroyed(),
    ).subscribe(page => { this.publishers.set(page.items); this.total.set(Number(page.total)); this.loading.set(false); });
  }

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.publisherService.getPublishers(this.pageIndex, this.pageSize, this.searchQuery || undefined).subscribe({
      next: page => { this.publishers.set(page.items); this.total.set(Number(page.total)); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  onSearch(v: string): void { this.search$.next(v); }
  onPage(e: PageEvent): void { this.pageIndex = e.pageIndex; this.pageSize = e.pageSize; this.load(); }

  private dialogData(p?: Publisher): SimpleEntityDialogData {
    return {
      title: p ? 'Edit Publisher' : 'Create Publisher',
      fields: [
        { key: 'name', label: 'Name', maxLength: 255 },
        { key: 'address', label: 'Address', maxLength: 255 },
      ],
      initialValues: p ? { name: p.name, address: p.address } : undefined,
    };
  }

  openCreate(): void {
    this.dialog.open(SimpleEntityFormDialog, { data: this.dialogData(), disableClose: true })
      .afterClosed().subscribe(v => { if (v) this.publisherService.createPublisher(v).subscribe(() => this.load()); });
  }

  openEdit(p: Publisher): void {
    this.dialog.open(SimpleEntityFormDialog, { data: this.dialogData(p), disableClose: true })
      .afterClosed().subscribe(v => { if (v) this.publisherService.updatePublisher(p.id!, v).subscribe(() => this.load()); });
  }

  openDelete(p: Publisher): void {
    this.dialog.open(ConfirmDialog, { data: { title: 'Delete Publisher?', message: 'This action cannot be undone. Are you sure you want to remove this publisher permanently?' } })
      .afterClosed().subscribe(ok => { if (ok) this.publisherService.deletePublisher(p.id!).subscribe(() => this.load()); });
  }
}
