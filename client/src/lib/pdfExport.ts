// Exportação PDF nativa via API window.print() com renderização de todas as seções.
// Estratégia: injetar classe `print-all` no body que, via CSS print, força a
// renderização sequencial de todas as seções em um único documento.

import { toast } from "sonner";

/**
 * Modo "Imprimir seção atual": comportamento padrão do browser print.
 */
export function exportCurrentSectionPDF() {
  toast.success("Abrindo diálogo de impressão...", {
    description: "Escolha 'Salvar como PDF' no destino para gerar o arquivo.",
  });
  setTimeout(() => window.print(), 250);
}

/**
 * Modo "Dossiê completo": renderiza todas as seções em sequência antes de
 * imprimir. Para isso navegamos por cada hash, aguardamos o paint, e ao final
 * inserimos a classe 'print-all' no body para que o CSS print mostre todos
 * os frames concatenados.
 *
 * Nota: como as seções são renderizadas com `key={active}`, precisamos usar
 * uma abordagem diferente — forçamos um clone do conteúdo em um container
 * print-only.
 */
export async function exportFullDossiePDF(
  sections: { id: string; label: string }[],
  setActive: (id: string) => void
) {
  const toastId = toast.loading(`Preparando dossiê completo (${sections.length} seções)...`);

  try {
    // Cria um container oculto com todas as seções renderizadas
    const container = document.createElement("div");
    container.id = "pdf-full-dossie";
    container.style.display = "none";
    document.body.appendChild(container);

    // Itera pelas seções, captura o HTML renderizado, empilha no container
    for (let i = 0; i < sections.length; i++) {
      const { id, label } = sections[i];
      toast.loading(
        `Renderizando ${i + 1}/${sections.length}: ${label}...`,
        { id: toastId }
      );
      setActive(id);
      // Aguarda o React renderizar + charts se montarem
      await new Promise((resolve) => setTimeout(resolve, 450));

      const main = document.querySelector("main");
      if (main) {
        const clone = main.cloneNode(true) as HTMLElement;
        const sectionWrapper = document.createElement("div");
        sectionWrapper.className = "pdf-section-break";
        sectionWrapper.innerHTML = `<h1 class="pdf-section-title">${label}</h1>`;
        sectionWrapper.appendChild(clone);
        container.appendChild(sectionWrapper);
      }
    }

    toast.success("Dossiê completo pronto. Abrindo impressão...", { id: toastId });

    // Ativa modo print-all (CSS escondido o original, mostra o container)
    document.body.classList.add("print-all-mode");
    await new Promise((resolve) => setTimeout(resolve, 200));

    window.print();

    // Cleanup após print
    setTimeout(() => {
      document.body.classList.remove("print-all-mode");
      container.remove();
    }, 1000);
  } catch (err) {
    toast.error("Erro ao gerar dossiê completo", {
      id: toastId,
      description: String(err),
    });
  }
}
