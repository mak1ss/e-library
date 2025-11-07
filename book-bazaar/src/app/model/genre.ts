export class Genre {
  constructor(
    public id?: number,
    public name?: string,
    public description?: string,
  ) {}

  public static fromObject(genre:Genre) {
    return new Genre(
      genre.id,
      genre.name,
      genre.description
    )
  }
}
