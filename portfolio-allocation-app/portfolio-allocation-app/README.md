# Portfolio Allocation App

This project is designed to help users determine the optimal allocation of their investment portfolio among equities, ETFs, and bonds. The application ensures that a majority of the portfolio is allocated to equities.

## Project Structure

```
portfolio-allocation-app
├── src
│   ├── app.ts                # Entry point of the application
│   ├── models
│   │   └── allocation.ts      # Contains the Allocation class
│   ├── services
│   │   └── calculator.ts      # Contains the allocation calculation logic
│   └── types
│       └── index.ts          # Defines input and output interfaces
├── package.json               # npm configuration file
├── tsconfig.json              # TypeScript configuration file
└── README.md                  # Project documentation
```

## Features

- **Equity Majority**: The application ensures that the equity allocation is the majority of the total portfolio.
- **Flexible Input**: Users can input their desired percentages for equities, ETFs, and bonds.
- **Validation**: The application validates the input percentages to ensure they sum up to 100%.

## Installation

To install the necessary dependencies, run:

```
npm install
```

## Usage

To start the application, use the following command:

```
npm start
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License.