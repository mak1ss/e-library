import { Component, effect, input, output, signal, SimpleChange, SimpleChanges } from '@angular/core';
import {Filter} from '../../utils/filter';
import {NgIf} from '@angular/common';
import {MatCheckbox} from '@angular/material/checkbox';
import {MatButton} from '@angular/material/button';

@Component({
  selector: 'app-filter-panel',
  imports: [
    NgIf,
    MatCheckbox,
    MatButton
  ],
  templateUrl: './filter-panel.html',
  styleUrl: './filter-panel.css',
})
export class FilterPanel {

  filters = input.required<Filter[]>();

  currentSelected = signal<Record<string, string[]>>({});

  selectedFilters = input<Record<string, string[]>>({});

  changed = output<Record<string, string[]>>();

  constructor() {
    effect(() => {
      if (this.selectedFilters) {
        const incoming = this.selectedFilters ?? {};
        this.currentSelected.set(incoming());
      }
    })
  }

  visibleOptions(filter: Filter): string[] {
    return filter.expanded
      ? filter.options
      : filter.options.slice(0, filter.defaultVisibleCount);
  }

  toggleOption(filterName: string, option: string) {
    const selected = this.currentSelected()[filterName] ?? [];

    if (selected.includes(option)) {
      this.currentSelected.update(filters => ({
        ...filters,
        [filterName]: selected.filter(o => o !== option)
      }));
    } else {
      this.currentSelected.update(filters => ({
        ...filters,
        [filterName]: [...selected, option]
      }));
    }

    this.changed.emit(this.currentSelected());
  }

  toggleExpanded(filterName: string) {
    const filter = this.filters().find(f => f.name === filterName);
    if (filter) filter.expanded = !filter.expanded;
  }

  isSelected(filterName: string, option: string): boolean {
    return this.currentSelected()[filterName]?.includes(option) ?? false;
  }

  clearFilters(): void {
    this.currentSelected.set({});
    this.changed.emit({});
  }
}
