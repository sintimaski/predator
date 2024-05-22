class RedisProtocolEncoder:
    def bulk_string(self, message):
        # $<length>\r\n<data>\r\n
        return f"${len(message)}\r\n{message}\r\n".encode()

    def simple_string(self, message):
        # +<data>\r\n
        return f"+{message}\r\n".encode()

    def integer(self, value: int | str):
        # :<value>\r\n
        return f":{value}\r\n".encode()

    def error(self):
        pass

    def array(self, items: list):
        # *<length>\r\n<item1><item2>...<itemN>\r\n
        encoded_items = b""
        for item in items:
            if isinstance(item, str):
                encoded_items += self.bulk_string(item)
            elif isinstance(item, int):
                encoded_items += self.integer(item)

        return f"*{len(items)}\r\n{encoded_items.decode()}".encode()


rpe = RedisProtocolEncoder()
