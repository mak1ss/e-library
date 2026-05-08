import { Component, inject, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';

export interface FieldConfig {
  key: string;
  label: string;
  maxLength: number;
  multiline?: boolean;
  required?: boolean;
}

export interface SimpleEntityDialogData {
  title: string;
  fields: FieldConfig[];
  initialValues?: Record<string, any>;
}

@Component({
  selector: 'app-simple-entity-form-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, MatDialogModule, MatButtonModule, MatIconModule, MatFormFieldModule, MatInputModule],
  templateUrl: './simple-entity-form-dialog.html',
})
export class SimpleEntityFormDialog implements OnInit {
  private fb = inject(FormBuilder);
  readonly dialogRef = inject(MatDialogRef<SimpleEntityFormDialog>);
  readonly data: SimpleEntityDialogData = inject(MAT_DIALOG_DATA);

  form = this.fb.group({});

  ngOnInit(): void {
    for (const field of this.data.fields) {
      const validators = field.required !== false ? [Validators.required, Validators.maxLength(field.maxLength)] : [Validators.maxLength(field.maxLength)];
      this.form.addControl(field.key, this.fb.control(this.data.initialValues?.[field.key] ?? '', validators));
    }
  }

  submit(): void {
    if (this.form.invalid) return;
    this.dialogRef.close(this.form.value);
  }

  getControl(key: string) {
    return this.form.get(key);
  }
}
