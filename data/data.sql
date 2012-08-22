insert into parameter(key_, is_email, is_notified, addressees) values ('system.cpu.load[,avg1]', 1, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees) values ('system.cpu.load[,avg5]', 1, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees) values ('system.cpu.load[,avg15]', 1, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees) values ('vm.memory.size[pfree]', 1, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees) values ('vm.memory.size_manual_pused[]', 1, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees, bound) values ('system.swap.size[,pfree]', 1, 1, '[]', 20);
insert into parameter(key_, is_email, is_notified, addressees) values ('system.cpu.util[,iowait,]', 1, 1, '[]');

insert into parameter(key_, is_email, is_notified, addressees) values ('system.cpu.load[,avg1]', 0, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees) values ('system.cpu.load[,avg5]', 0, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees) values ('system.cpu.load[,avg15]', 0, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees) values ('vm.memory.size[pfree]', 0, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees) values ('vm.memory.size_manual_pused[]', 0, 1, '[]');
insert into parameter(key_, is_email, is_notified, addressees, bound) values ('system.swap.size[,pfree]', 0, 1, '[]', 20);
insert into parameter(key_, is_email, is_notified, addressees) values ('system.cpu.util[,iowait,]', 0, 1, '[]');

insert into item_info(key_, is_minimized) values ('system.cpu.load[,avg1]', 1);
insert into item_info(key_, is_minimized) values ('system.cpu.load[,avg5]', 1);
insert into item_info(key_, is_minimized) values ('system.cpu.load[,avg15]', 1);
insert into item_info(key_, is_minimized) values ('vm.memory.size[pfree]', 0);
insert into item_info(key_, is_minimized) values ('vm.memory.size_manual_pused[]', 0);
insert into item_info(key_, is_minimized) values ('system.swap.size[,pfree]', 0);
insert into item_info(key_, is_minimized) values ('system.cpu.util[,iowait,]', 0);
