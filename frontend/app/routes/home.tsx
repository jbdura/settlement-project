import type { Route } from "./+types/home";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Settlement RDMBS" },
    { name: "description", content: "Test RDMS" },
  ];
}

export default function Home() {
  return (
    <>
      <h1>Welcome to React Router</h1>
    </>
  );
}
