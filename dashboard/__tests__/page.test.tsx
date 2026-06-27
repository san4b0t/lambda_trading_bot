import { render, screen, act } from "@testing-library/react";
import Dashboard from "../app/page";

// Mock the native browser WebSocket
class MockWebSocket {
  // 1. Create a static property to hold the active instance
  static activeInstance: MockWebSocket;

  onopen: () => void = () => {};
  onmessage: (event: any) => void = () => {};
  onclose: () => void = () => {};
  close() {}

  constructor(public url: string) {
    // 2. Save 'this' instance the moment React calls 'new WebSocket()'
    MockWebSocket.activeInstance = this;
    setTimeout(() => this.onopen(), 10);
  }

  // Helper method to simulate receiving a message from the Python server
  simulateMessage(data: any) {
    this.onmessage({ data: JSON.stringify(data) });
  }
}

// Replace the global WebSocket with our mock
(global as any).WebSocket = MockWebSocket;

describe("Dashboard Component", () => {
  it("renders initial state correctly", () => {
    render(<Dashboard />);
    expect(screen.getByText("System Diagnostics")).toBeInTheDocument();
    expect(screen.getByText("$0.00")).toBeInTheDocument();
  });

  it("updates price when a websocket message is received", async () => {
    render(<Dashboard />);

    // Grab the instance of the MockWebSocket that React just created
    const wsInstance = MockWebSocket.activeInstance;

    // Simulate receiving a market tick from Python
    act(() => {
      wsInstance.simulateMessage({
        topic: "market_data",
        data: { symbol: "BTC/USDT", price: 45123.5, side: "buy" },
      });
    });

    // Check if the React UI updated the price
    expect(await screen.findByText("$45123.50")).toBeInTheDocument();
    expect(await screen.findByText("buy")).toBeInTheDocument();
  });
});
