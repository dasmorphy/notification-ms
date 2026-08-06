from string import Template


class NotificationTemplate:

    # Cada entrada: title y body con placeholders estilo $variable
    TEMPLATES: dict[str, dict[str, str]] = {
        "TECHNICAL_APPROVAL_REQUEST_REJECTED": {
            "title": "Solicitud rechazada",
            "body": "$username ha rechazado tu solicitud de finalización de proyecto",
        },
        "TECHNICAL_APPROVAL_REQUEST_APPROVED": {
            "title": "Solicitud aprobada",
            "body": "$username ha aprobado tu solicitud de finalización de proyecto",
        },
        # agrega aquí nuevos tipos según los necesites
    }

    def has_template(self, notification_type: str) -> bool:
        return notification_type in self.TEMPLATES

    def render(self, notification_type: str, variables: dict) -> tuple[str, str]:
        """
        Devuelve (title, body) ya renderizados.
        Lanza KeyError si falta alguna variable requerida por la plantilla.
        """
        template = self.TEMPLATES[notification_type]
        variables = variables or {}

        try:
            title = Template(template["title"]).substitute(variables)
            body = Template(template["body"]).substitute(variables)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(
                f"Falta la variable '{missing_var}' requerida para la plantilla "
                f"del tipo '{notification_type}'"
            )

        return title, body