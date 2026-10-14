export interface SamplePoem {
  titulo: string;
  autor: string;
  texto: string;
  descripcion: string;
}

export const SAMPLE_POEMS: SamplePoem[] = [
  {
    titulo: 'Soneto del Alba',
    autor: 'R.L. Stevenson',
    descripcion: 'Lírica clásica sobre la noche y el amanecer',
    texto: `Era noche oscura, y tranquila...
Y el viento susurraba en las ramas;
Una estrella palpitante parpadeaba en la calma.
¡Ay! ¡Cómo lloraba yo!

Y el alba dorada apareció,
Desatando los grillos del sueño;
El amanecer llegó con su fulgor.`,
  },
  {
    titulo: 'La Cenicienta',
    autor: 'Anónimo',
    descripcion: 'Narración poética tradicional',
    texto: `Había una vez un pobre hombre
con una casa y una pequeña parcela.
Él tenía tres hijas muy lindas,
Pero la más joven era la más triste.

Su madre había muerto hace mucho tiempo,
Deja huérfana a las niñas en soledad.
Y ella trabajaba duro cada día,
Limpiando y sirviendo a su familia.`,
  },
  {
    titulo: 'El Viaje',
    autor: 'Poema original',
    descripcion: 'Versos sobre el horizonte marino y el viaje',
    texto: `El mar se extendía ante mis ojos,
Olas saltaban contra la roca gris;
El viento me cantaba historias antiguas,
De navegantes que antes vivieron aquí.

Los pájaros volaban en formación,
Sobre el horizonte azul y sereno;
La tierra me llamaba desde lejos,
Pero yo tenía que seguir yendo.`,
  },
];
