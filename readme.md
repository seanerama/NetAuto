

```
# Network Management Application

This project is a network management application built using multiple Docker containers running FastAPI servers. Each container is responsible for handling interaction with a different system such as Webex, SolarWinds, ServiceNow, DNA Center, and SSH/SCP.

## Project Structure


network-management-app/
│
├── central/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│
├── webex/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│
├── solarwinds/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│
├── servicenow/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│
├── dnacenter/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│
├── sshscp/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│
├── docker-compose.yml
├── config.yaml
└── README.md
```

## Setup

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/network-management-app.git
   cd network-management-app
   ```

2. Create the `config.yaml` file and add your configuration details:
   ```yaml
   servicenow:
     base_url: "https://example.service-now.com"
     username: "your_servicenow_username"
     password: "your_servicenow_password"

   network_devices:
     cli_username: "network_cli_user"
     cli_password: "network_cli_password"

   dna_center:
     base_url: "https://dnacenter.example.com"
     api_username: "dna_api_user"
     api_password: "dna_api_password"
   email:
     send_server: 'smtp.domain.com'
     from_email: 'netauto-test@domain.com'
   ```
2. Create the `.env` file and add your configuration details:
   ```
   DNS_SERVER_1=8.8.8.4
   DNS_SERVER_2=8.8.8.8
   ```

4. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

## Usage

- **Webex Service**: Access at `http://localhost:8001`
- **SolarWinds Service**: Access at `http://localhost:8002`
- **ServiceNow Service**: Access at `http://localhost:8003`
- **DNA Center Service**: Access at `http://localhost:8004`
- **SSH/SCP Service**: Access at `http://localhost:8005`
- **Central Management Service**: Access at `http://localhost:8000`

### Example Endpoints

- **Get Status of Webex Service**:
  ```bash
  curl http://localhost:8001/status
  ```

- **Get Status of Central Management Service**:
  ```bash
  curl http://localhost:8000/status/webex
  ```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please reach out to [sdmahoney01@gmail.com](mailto:sdmahoney01@gmail.com).
```




This `README.md` file provides a comprehensive overview and instructions for setting up and using your network management application. If you need further customization or additional sections, feel free to ask!


