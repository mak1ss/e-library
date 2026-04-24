import { Component, computed, effect, input, output, signal, SimpleChange, SimpleChanges } from '@angular/core';
import {Filter} from '../../utils/filter';
import {NgIf, CommonModule} from '@angular/common';
import {MatCheckbox} from '@angular/material/checkbox';
import {MatButton} from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-filter-panel',
  imports: [
    NgIf,
    CommonModule,
    MatCheckbox,
    MatButton,
    MatIcon,
    FormsModule
  ],
  templateUrl: './filter-panel.html',
  styleUrl: './filter-panel.css',
})
export class FilterPanel {

  filters = input.required<Filter[]>();

  currentSelected = signal<Record<string, string[]>>({});

  selectedFilters = input<Record<string, string[]>>({});

  changed = output<Record<string, string[]>>();

  // Сигнали для пошуку в кожному фільтрі
  searchTexts = signal<Record<string, string>>({});

  hasSelectedFilters = computed(() => {
    const selected = this.currentSelected();
    return Object.values(selected).some(arr => arr && arr.length > 0);
  });
  
  constructor() {
    effect(() => {
      if (this.selectedFilters) {
        const incoming = this.selectedFilters ?? {};
        this.currentSelected.set(incoming());
      }
    })
  }

  visibleOptions(filter: Filter): string[] {
    const searchText = this.searchTexts()[filter.name]?.toLowerCase() || '';
    let filtered = filter.options;

    // Якщо є пошук, фільтруємо за ним
    if (searchText) {
      filtered = filter.options.filter(option =>
        option.toLowerCase().includes(searchText)
      );
    } else {
      // Якщо пошук порожній
      // - Якщо розгорнутий, показуємо ВСІ елементи
      // - Якщо згорнутий, показуємо тільки перші defaultVisibleCount
      if (!filter.expanded) {
        filtered = filter.options.slice(0, filter.defaultVisibleCount);
      }
    }

    return filtered;
  }

  updateSearchText(filterName: string, text: string) {
    this.searchTexts.update(texts => ({
      ...texts,
      [filterName]: text
    }));
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
    if (filter) {
      filter.expanded = !filter.expanded;
      // Очищуємо пошук при згортанні
      if (!filter.expanded) {
        this.updateSearchText(filterName, '');
      }
    }
  }

  isSelected(filterName: string, option: string): boolean {
    return this.currentSelected()[filterName]?.includes(option) ?? false;
  }

  clearFilters(): void {
    this.currentSelected.set({});
    this.changed.emit({});
  }
}
