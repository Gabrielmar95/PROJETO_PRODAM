import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";

function Router() {
  // S3-M02: rotas wouter dedicadas para cada seção do dashboard.
  // /secao/:id renderiza Home com a seção selecionada; / continua
  // sendo o painel inicial. Bookmarks legados via /#painel continuam
  // funcionando porque Home mantém handler de hashchange.
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/secao/:id"} component={Home} />
      <Route path={"/404"} component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <TooltipProvider>
          <Toaster theme="dark" />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
