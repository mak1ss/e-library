import { Component } from '@angular/core';
import {Filter} from '../../utils/filter';
import {NgIf} from '@angular/common';
import {MatCheckbox} from '@angular/material/checkbox';
import {MatRipple} from '@angular/material/core';
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
  filters: Filter[] = [
    {
      name: 'authors',
      label: 'Authors',
      options: ['Rowling', 'Tolkien', 'Gaiman', 'Orwell', 'Murakami', 'Austen', 'King'],
      defaultVisibleCount: 4,
      expanded: false,
    },
    {
      name: 'genres',
      label: 'Genres',
      options: ['Фантастика', 'Детектив', 'Роман', 'Фентезі', 'Трилер', 'Драма'],
      defaultVisibleCount: 3,
      expanded: false,
    },
  ];

  selected: Record<string, string[]> = {};

  visibleOptions(filter: Filter): string[] {
    return filter.expanded
      ? filter.options
      : filter.options.slice(0, filter.defaultVisibleCount);
  }

  toggleOption(filterName: string, option: string) {
    const selected = this.selected[filterName] ?? [];

    if (selected.includes(option)) {
      this.selected[filterName] = selected.filter(o => o !== option);
    } else {
      this.selected[filterName] = [...selected, option];
    }
  }

  toggleExpanded(filterName: string) {
    const filter = this.filters.find(f => f.name === filterName);
    if (filter) filter.expanded = !filter.expanded;
  }

  isSelected(filterName: string, option: string): boolean {
    return this.selected[filterName]?.includes(option) ?? false;
  }

  clearFilters(): void {
    this.selected = {};
  }
}
