import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

export interface ConfirmDialogData {
  title?: string;
  message?: string;
}

@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule],
  template: `
    <div class="p-6 bg-white">
      <h2 class="text-xl font-serif font-bold text-gray-900 mb-2 leading-tight">
        {{ data.title ?? 'Delete?' }}
      </h2>

      <p class="text-gray-500 mb-8 text-base leading-relaxed">
        {{ data.message ?? 'This action cannot be undone. Are you sure?' }}
      </p>

      <div class="flex justify-end gap-3">
        <button mat-button
                (click)="dialogRef.close(false)"
                class="!font-medium !text-gray-600 hover:!bg-gray-50 !rounded-full">
          Cancel
        </button>

        <button mat-flat-button
                color="warn"
                (click)="dialogRef.close(true)"
                class="!rounded-full !px-6 shadow-md shadow-red-100">
          Delete
        </button>
      </div>
    </div>
  `,
  styles: [`:host { display: block; background: white; }`]
})
export class ConfirmDialog {
  readonly dialogRef = inject(MatDialogRef<ConfirmDialog>);
  readonly data: ConfirmDialogData = inject(MAT_DIALOG_DATA, { optional: true }) ?? {};
}
